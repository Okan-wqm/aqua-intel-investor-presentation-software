import paramiko, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('142.93.109.162', username='root', password='Trond123**', timeout=10, allow_agent=False, look_for_keys=False)

cmds = [
    # Install certbot
    'apt-get install -y -qq certbot python3-certbot-nginx',

    # Get certificate (IP-only won't work with Let's Encrypt - need domain)
    # For IP-only, create self-signed cert
    'mkdir -p /etc/nginx/ssl',
    'openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -keyout /etc/nginx/ssl/selfsigned.key -out /etc/nginx/ssl/selfsigned.crt -subj "/CN=142.93.109.162"',

    # Update nginx config with SSL
    '''cat > /etc/nginx/sites-available/aquaintel << 'CONF'
server {
    listen 80;
    server_name 142.93.109.162;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name 142.93.109.162;
    client_max_body_size 10M;

    ssl_certificate /etc/nginx/ssl/selfsigned.crt;
    ssl_certificate_key /etc/nginx/ssl/selfsigned.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

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

    # Test and restart nginx
    'nginx -t && systemctl restart nginx',

    # Verify
    'sleep 2 && curl -sk -o /dev/null -w "%{http_code}" https://127.0.0.1/login/',
]

for cmd in cmds:
    short = cmd.strip()[:120]
    print(f'\n>>> {short}{"..." if len(cmd.strip())>120 else ""}')
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=60)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out.strip(): print(out.strip())
    if err.strip(): print(f'[err] {err.strip()}')

ssh.close()
print('\n=== SSL DONE ===')
