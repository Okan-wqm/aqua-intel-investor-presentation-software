import paramiko, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('142.93.109.162', username='root', password='Trond123**', timeout=10, allow_agent=False, look_for_keys=False)

cmds = [
    # Update CSRF trusted origins for https
    '''cd /opt/aquaintel/app && sed -i "s|CSRF_TRUSTED_ORIGINS.*|CSRF_TRUSTED_ORIGINS = ['http://142.93.109.162', 'https://142.93.109.162']|" aqua_intel/settings.py''',

    # Add SECURE_PROXY_SSL_HEADER
    '''grep -q SECURE_PROXY_SSL_HEADER /opt/aquaintel/app/aqua_intel/settings.py || echo "SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')" >> /opt/aquaintel/app/aqua_intel/settings.py''',

    # Restart
    'systemctl restart aquaintel',
    'sleep 2 && curl -sk -o /dev/null -w "%{http_code}" https://127.0.0.1/login/',

    # Verify certbot timer for auto-renewal (already installed)
    'systemctl is-enabled certbot.timer && systemctl status certbot.timer --no-pager | head -5',
]

for cmd in cmds:
    print(f'\n>>> {cmd.strip()[:100]}')
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out.strip(): print(out.strip())
    if err.strip(): print(f'[err] {err.strip()}')

ssh.close()
