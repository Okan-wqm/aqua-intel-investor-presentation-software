import paramiko, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('142.93.109.162', username='root', password='Trond123**', timeout=10, allow_agent=False, look_for_keys=False)

script = """
import django, os
os.environ['DJANGO_SETTINGS_MODULE'] = 'aqua_intel.settings'
django.setup()
from django.contrib.auth.models import User

# List all users
for u in User.objects.all():
    print(f'User: {u.username}, active: {u.is_active}, super: {u.is_superuser}')

# Delete all and create fresh
User.objects.all().delete()
u = User(username='admin', is_staff=True, is_superuser=True, is_active=True)
u.set_password('admin123')
u.save()

# Verify
u2 = User.objects.get(username='admin')
print(f'Created: {u2.username}, check_password: {u2.check_password("admin123")}')
"""

cmd = "cd /opt/aquaintel/app && cat << 'PYEOF' | ./venv/bin/python\n" + script + "\nPYEOF"
stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
print(stdout.read().decode())
err = stderr.read().decode()
if err.strip():
    print('ERR:', err)
ssh.close()
