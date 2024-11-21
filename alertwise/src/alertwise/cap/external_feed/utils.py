import logging

import feedparser
import requests
from alertwise.capeditor.caputils import cap_xml_to_alert_data
from capvalidator import validate_cap_message

from alertwise.cap.utils import create_draft_alert_from_alert_data
from .models import ExternalAlertFeed, ExternalAlertFeedEntry

logger = logging.getLogger(__name__)


def fetch_and_process_feed(feed_id):
    # get feed by id
    external_feed = ExternalAlertFeed.objects.get(id=feed_id)
    url = external_feed.url
    submit_for_moderation = external_feed.submit_for_moderation
    
    # get remote feed content
    feed = feedparser.parse(url)
    
    entries = feed.entries
    
    # extract alert entries
    for entry in entries:
        entry_id = entry.id
        entry_link = entry.link
        
        if not entry_id or not entry_link:
            logger.error(f"[EXTERNAL FEED] Entry with missing ID or Link. Skipping...")
            continue
        
        # check if entry link is a .xml link
        if not entry_link.endswith('.xml'):
            logger.info(f"[EXTERNAL FEED] Link: {entry_link} does not seem to be a CAP alert XML "
                        f"file since it does not end with .xml. Skipping...")
            continue
        
        logger.info(f"[EXTERNAL FEED] Processing feed entry with ID: {entry_id}, Link: {entry_link}")
        # check if alert with this entry_id has already been imported.
        # Quick check to avoid fetching the CAP alert XML, assuming that the entry_link will always be unique
        exists = ExternalAlertFeedEntry.objects.filter(url=entry_link).exists()
        if exists:
            logger.info(f"[EXTERNAL FEED] Alert from {entry_link} was already imported. Skipping...")
            continue
        
        logger.info(f"[EXTERNAL FEED] Fetching CAP alert XML from {entry_link}")
        # fetch CAP alert XML
        r = requests.get(entry_link)
        r.raise_for_status()
        xml_bytes = r.content
        
        logger.info(f"[EXTERNAL FEED] Validating CAP alert XML from {entry_link}. "
                    f"Signature check enabled: {external_feed.validate_xml_signature} ")
        
        # validate CAP alert XML
        result = validate_cap_message(xml_bytes, strict=external_feed.validate_xml_signature)
        if not result.passed:
            logger.error(f"[EXTERNAL FEED] CAP validation failed for {entry_link}: {result.message}")
            continue
        
        logger.info(f"[EXTERNAL FEED] CAP validation passed for {entry_link}")
        
        logger.info(f"[EXTERNAL FEED] Parsing CAP alert XML from {entry_link}")
        alert_data = cap_xml_to_alert_data(xml_bytes, validate=False)
        
        alert_identifier = alert_data.get('identifier')
        
        # check if alert with this identifier has already been imported
        exists = ExternalAlertFeedEntry.objects.filter(remote_alert_id=alert_identifier).exists()
        if exists:
            logger.info(f"[EXTERNAL FEED] Alert with identifier {alert_identifier} was already imported. Skipping...")
            continue
        
        logger.info(f"[EXTERNAL FEED] Creating draft alert from CAP alert data for {entry_link}")
        # create draft alert page from alert data
        imported_alert = create_draft_alert_from_alert_data(alert_data, submit_for_moderation=submit_for_moderation)
        
        logger.info(f"[EXTERNAL FEED] Creating ExternalAlertFeedEntry for {entry_link}")
        if imported_alert:
            ExternalAlertFeedEntry.objects.create(
                feed=external_feed,
                remote_alert_id=alert_identifier,
                url=entry_link,
                imported_alert=imported_alert
            )
