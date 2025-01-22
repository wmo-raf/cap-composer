from django.core.management.base import BaseCommand

from alertwise.cap.models import CapAlertPage
from alertwise.cap.utils import create_cap_alert_multi_media
from django.db.models import Q


class Command(BaseCommand):
    help = "Create CAP alert Multi Media content for CAP Alerts without Multi Media content generated."
    
    def handle(self, *args, **options):
        # Get all CAP Alerts without Multi Media content
        cap_alerts = CapAlertPage.objects.all().live().filter(
            Q(alert_area_map_image__isnull=True) | Q(alert_pdf_preview__isnull=True), status="Actual", )
        
        if not cap_alerts.exists():
            print("No CAP Alerts without Multi Media content found. Exiting...")
            return
        
        count = cap_alerts.count()
        
        print(f"Processing {count} CAP Alerts")
        
        for i, cap_alert in enumerate(cap_alerts):
            print(f"[{i + 1}/{count}] Processing CAP Alert: {cap_alert.title}")
            create_cap_alert_multi_media(cap_alert.id, clear_cache_on_success=True)
            print(f"[{i + 1}/{count}] Completed processing CAP Alert: {cap_alert.title}")
