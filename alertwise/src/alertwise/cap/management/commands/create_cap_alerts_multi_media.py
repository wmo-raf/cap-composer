from django.core.management.base import BaseCommand

from cap.models import CapAlertPage
from cap.utils import create_cap_alert_multi_media


class Command(BaseCommand):
    help = "Create CAP alert Multi Media content for CAP Alerts without Multi Media content generated."
    
    def handle(self, *args, **options):
        cap_alerts = CapAlertPage.objects.all().live().filter(status="Actual", alert_area_map_image__isnull=True)
        
        if not cap_alerts.exists():
            print("No CAP Alerts without Multi Media content found. Exiting...")
            return
        
        count = cap_alerts.count()
        
        print(f"Processing {count} CAP Alerts")
        
        for i, cap_alert in enumerate(cap_alerts):
            print(f"[{i + 1}/{count}] Processing CAP Alert: {cap_alert.title}")
            create_cap_alert_multi_media(cap_alert.id)
            print(f"[{i + 1}/{count}] Completed processing CAP Alert: {cap_alert.title}")
