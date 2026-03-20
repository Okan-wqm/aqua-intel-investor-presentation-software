import paramiko, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('142.93.109.162', username='root', password='Trond123**', timeout=10, allow_agent=False, look_for_keys=False)

cmds = [
    # 1. Check login works internally
    '''cd /opt/aquaintel/app && ./venv/bin/python -c "
import django,os
os.environ['DJANGO_SETTINGS_MODULE']='aqua_intel.settings'
django.setup()
from django.contrib.auth import authenticate
u=authenticate(username='admin',password='admin123')
print('authenticate result:',u)
"''',

    # 2. Check CSRF and session settings - add CSRF_TRUSTED_ORIGINS
    '''grep -c CSRF_TRUSTED /opt/aquaintel/app/aqua_intel/settings.py || echo "MISSING"''',

    # 3. Add CSRF trusted origins and fix settings
    '''cat >> /opt/aquaintel/app/aqua_intel/settings.py << 'EOF'

# Production fixes
CSRF_TRUSTED_ORIGINS = ['http://142.93.109.162', 'https://142.93.109.162']
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
EOF''',

    # 4. Restart gunicorn
    'systemctl restart aquaintel',

    # 5. Test login with curl
    '''sleep 2 && curl -s -c /tmp/cookies.txt http://127.0.0.1:8000/login/ | grep -o 'csrfmiddlewaretoken" value="[^"]*"' | head -1''',

    # 6. Try actual login
    '''CSRF=$(curl -s -c /tmp/cookies.txt http://127.0.0.1:8000/login/ | grep -oP 'csrfmiddlewaretoken" value="\K[^"]+') && curl -s -b /tmp/cookies.txt -c /tmp/cookies.txt -X POST -d "username=admin&password=admin123&csrfmiddlewaretoken=$CSRF" -H "Referer: http://127.0.0.1:8000/login/" -o /dev/null -w "%{http_code} redirect:%{redirect_url}" http://127.0.0.1:8000/login/''',
]

for cmd in cmds:
    print(f'\n>>> {cmd.strip()[:100]}...' if len(cmd.strip())>100 else f'\n>>> {cmd.strip()}')
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out.strip(): print(out.strip())
    if err.strip(): print(f'[err] {err.strip()}')

ssh.close()
