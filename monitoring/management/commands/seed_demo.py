from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from monitoring.models import Field, FieldUpdate


class Command(BaseCommand):
    help = "Seed demo users and sample fields for the SmartSeason assessment."

    def handle(self, *args, **options):
        User = get_user_model()

        admin_user, _ = User.objects.get_or_create(
            username="admin",
            defaults={
                "first_name": "System",
                "last_name": "Coordinator",
                "role": User.Role.ADMIN,
                "is_staff": True,
                "is_superuser": True,
                "email": "admin@smartseason.local",
            },
        )
        if not admin_user.check_password("admin123"):
            admin_user.set_password("admin123")
        admin_user.role = User.Role.ADMIN
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()

        agent_user, _ = User.objects.get_or_create(
            username="agent1",
            defaults={
                "first_name": "Field",
                "last_name": "Agent",
                "role": User.Role.FIELD_AGENT,
                "email": "agent1@smartseason.local",
            },
        )
        if not agent_user.check_password("agent123"):
            agent_user.set_password("agent123")
        agent_user.role = User.Role.FIELD_AGENT
        agent_user.save()

        if not Field.objects.exists():
            maize = Field.objects.create(
                name="North Ridge",
                crop_type="Maize",
                planting_date=date.today() - timedelta(days=22),
                current_stage=Field.Stage.GROWING,
                assigned_agent=agent_user,
            )
            beans = Field.objects.create(
                name="Valley Plot",
                crop_type="Beans",
                planting_date=date.today() - timedelta(days=8),
                current_stage=Field.Stage.PLANTED,
                assigned_agent=agent_user,
            )
            tea = Field.objects.create(
                name="River Bank",
                crop_type="Tea",
                planting_date=date.today() - timedelta(days=91),
                current_stage=Field.Stage.HARVESTED,
                assigned_agent=None,
            )
            FieldUpdate.objects.create(field=maize, updated_by=agent_user, stage=Field.Stage.GROWING, notes="Healthy stand with good moisture.")
            FieldUpdate.objects.create(field=beans, updated_by=agent_user, stage=Field.Stage.PLANTED, notes="Emergence observed on most rows.")
            FieldUpdate.objects.create(field=tea, updated_by=admin_user, stage=Field.Stage.HARVESTED, notes="Harvest completed and sent to storage.")

        self.stdout.write(self.style.SUCCESS("Demo data ready. Use admin/admin123 and agent1/agent123."))
