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
User.objects.filter(username='admin').delete()
u = User.objects.create_superuser('admin', 'admin@aquaintel.com', 'admin123')
print('OK user created:', u.username)
"""

cmd = "cd /opt/aquaintel/app && cat << 'PYEOF' | ./venv/bin/python\n" + script + "\nPYEOF"
stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())
ssh.close()
