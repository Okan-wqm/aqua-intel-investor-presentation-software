"""Deploy script — runs commands on remote server via SSH."""
import paramiko
import sys

HOST = '142.93.109.162'
USER = 'root'
PASS = 'Trond123**'

def ssh_run(commands, timeout=120):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASS, timeout=10, allow_agent=False, look_for_keys=False)
    for cmd in commands:
        print(f'\n>>> {cmd}')
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
        out = stdout.read().decode()
        err = stderr.read().decode()
        if out.strip():
            print(out.strip())
        if err.strip():
            print(f'[stderr] {err.strip()}')
    ssh.close()

if __name__ == '__main__':
    phase = sys.argv[1] if len(sys.argv) > 1 else 'full'

    if phase in ('full', 'setup'):
        print('=== SETUP ===')
        ssh_run([
            'apt-get update -qq && apt-get install -y -qq python3-venv python3-pip nginx git',
            'mkdir -p /opt/aquaintel',
            f'cd /opt/aquaintel && (git clone https://github.com/Okan-wqm/aqua-intel-investor-presentation-software.git app 2>/dev/null || (cd app && git pull origin master))',
            'cd /opt/aquaintel/app && python3 -m venv venv',
            'cd /opt/aquaintel/app && ./venv/bin/pip install -q django gunicorn',
            'cd /opt/aquaintel/app && ./venv/bin/python manage.py migrate --run-syncdb',
            'cd /opt/aquaintel/app && echo "from django.contrib.auth.models import User; User.objects.filter(username=\'admin\').exists() or User.objects.create_superuser(\'admin\',\'admin@aquaintel.com\',\'admin123\')" | ./venv/bin/python manage.py shell',
        ], timeout=180)

    if phase in ('full', 'gunicorn'):
        print('\n=== GUNICORN SERVICE ===')
        ssh_run([
            '''cat > /etc/systemd/system/aquaintel.service << 'UNIT'
[Unit]
Description=Aqua Intel Gunicorn
After=network.target

[Service]
User=root
WorkingDirectory=/opt/aquaintel/app
ExecStart=/opt/aquaintel/app/venv/bin/gunicorn aqua_intel.wsgi:application --bind 127.0.0.1:8000 --workers 3 --timeout 120
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
UNIT''',
            'systemctl daemon-reload && systemctl enable aquaintel && systemctl restart aquaintel',
            'sleep 2 && systemctl status aquaintel --no-pager | head -15',
        ])

    if phase in ('full', 'nginx'):
        print('\n=== NGINX CONFIG ===')
        ssh_run([
            '''cat > /etc/nginx/sites-available/aquaintel << 'CONF'
server {
    listen 80;
    server_name 142.93.109.162;
    client_max_body_size 10M;

    location /static/ {
        alias /opt/aquaintel/app/static/;
        expires 7d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }
}
CONF''',
            'ln -sf /etc/nginx/sites-available/aquaintel /etc/nginx/sites-enabled/',
            'rm -f /etc/nginx/sites-enabled/default',
            'nginx -t && systemctl restart nginx',
        ])

    if phase in ('full', 'update'):
        print('\n=== UPDATE (git pull + restart) ===')
        ssh_run([
            'cd /opt/aquaintel/app && git pull origin master',
            'cd /opt/aquaintel/app && ./venv/bin/python manage.py migrate --run-syncdb',
            'systemctl restart aquaintel',
            'sleep 2 && curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/login/',
        ])

    print('\n=== DONE ===')
