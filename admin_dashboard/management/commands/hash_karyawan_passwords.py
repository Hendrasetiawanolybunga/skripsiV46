from django.core.management.base import BaseCommand
from admin_dashboard.models import Karyawan
from django.contrib.auth.hashers import identify_hasher

class Command(BaseCommand):
    help = 'Re-hash Karyawan plaintext passwords saved in DB (if any). Hashes passwords that do not appear to be hashed.'

    def handle(self, *args, **options):
        count = 0
        for k in Karyawan.objects.all():
            pwd = k.password or ''
            needs_hash = True
            if pwd:
                # If the password contains '$', try to see if it's a valid Django hash
                if '$' in pwd:
                    try:
                        identify_hasher(pwd)
                        needs_hash = False
                    except Exception:
                        needs_hash = True
            if needs_hash and pwd:
                raw = pwd
                k.set_password(raw)
                k.save()
                count += 1
                self.stdout.write(f'Hashed password for {k.email}')
        self.stdout.write(self.style.SUCCESS(f'Done. Re-hashed {count} account(s).'))
