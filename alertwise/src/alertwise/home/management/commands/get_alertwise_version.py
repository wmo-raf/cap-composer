from django.core.management.base import BaseCommand

from alertwise.utils.version import get_complete_version, get_semver_version


class Command(BaseCommand):
    help = "Get AlertWise version"
    
    def handle(self, *args, **options):
        complete_version = get_complete_version()
        version = get_semver_version(complete_version)
        self.stdout.write(version)
