import paramiko, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('142.93.109.162', username='root', password='Trond123**', timeout=10, allow_agent=False, look_for_keys=False)

DOMAIN = 'aqua-intel.duckdns.org'

cmds = [
    # 1. Update nginx for domain (HTTP only first for certbot)
    f'''cat > /etc/nginx/sites-available/aquaintel << 'CONF'
server {{
    listen 80;
    server_name {DOMAIN} 142.93.109.162;
    client_max_body_size 10M;

    location /static/ {{
        alias /opt/aquaintel/app/static/;
        expires 7d;
    }}

    location / {{
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }}
}}
CONF''',

    'nginx -t && systemctl restart nginx',

    # 2. Get Let's Encrypt certificate
    f'certbot --nginx -d {DOMAIN} --non-interactive --agree-tos --email admin@aquaintel.com --redirect',

    # 3. Update Django ALLOWED_HOSTS and CSRF
    f'''cd /opt/aquaintel/app && sed -i "s|ALLOWED_HOSTS.*|ALLOWED_HOSTS = ['142.93.109.162', 'localhost', '127.0.0.1', '{DOMAIN}']|" aqua_intel/settings.py''',
    f'''cd /opt/aquaintel/app && sed -i "s|CSRF_TRUSTED_ORIGINS.*|CSRF_TRUSTED_ORIGINS = ['http://142.93.109.162', 'https://142.93.109.162', 'http://{DOMAIN}', 'https://{DOMAIN}']|" aqua_intel/settings.py''',

    # 4. Restart app
    'systemctl restart aquaintel',

    # 5. Verify
    f'sleep 2 && curl -s -o /dev/null -w "%{{http_code}}" https://{DOMAIN}/login/',

    # 6. Check auto-renewal
    'certbot renew --dry-run 2>&1 | tail -3',
]

for cmd in cmds:
    short = cmd.strip().split('\n')[0][:100]
    print(f'\n>>> {short}')
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=60)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out.strip(): print(out.strip())
    if err.strip(): print(f'[err] {err.strip()}')

ssh.close()
print('\n=== DOMAIN + SSL DONE ===')
