from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User


class Command(BaseCommand):
    help = 'Create clearance role groups and example users (finance, qa, me)'

    def handle(self, *args, **options):
        groups = ['finance', 'qa', 'me']
        for g in groups:
            Group.objects.get_or_create(name=g)
            self.stdout.write(self.style.SUCCESS(f'Ensured group: {g}'))

        # create example users
        users = [
            ('fin_officer', 'finance'),
            ('qa_user', 'qa'),
            ('me_user', 'me'),
        ]
        for username, group in users:
            u, created = User.objects.get_or_create(username=username, defaults={'email': f'{username}@example.com', 'is_staff': True})
            if created:
                u.set_password('ChangeMe123!')
                u.save()
            grp = Group.objects.get(name=group)
            u.groups.add(grp)
            self.stdout.write(self.style.SUCCESS(f'Ensured user {username} in group {group}'))
