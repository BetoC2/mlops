import boto3
import paramiko

# Crear una sesión de boto3
ec2_client = boto3.client('ec2', region_name='us-east-2')

# Leer IPs de los slaves
try:
    with open('slaves_ip.txt', 'r') as f:
        slave_ips = [line.strip() for line in f if line.strip()]
except Exception as e:
    print(f"Error al leer 'slaves_ip.txt': {e}")

print("IPs de slaves encontradas:", slave_ips)

try:
    with open('master_ip.txt', 'r') as f:
        master_ip = f.readline().strip()
except Exception as e:
    print(f"Error al leer 'master_ip.txt': {e}")

print("IP del master encontrada:", master_ip)

# Configurar la conexión SSH
key_path = 'id_rsa'
key = paramiko.RSAKey.from_private_key_file(key_path)
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Conectar a la instancia 'master' via SSH
ssh_client.connect(master_ip, username='ec2-user', pkey=key)

# Crear archivo de configuración de NGINX
nginx_config = f"""
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {{
    worker_connections 1024;
}}

http {{
    log_format custom '$remote_addr - $remote_user [$time_local] '
                      '"$request" $status $body_bytes_sent '
                      '"$http_referer" "$http_user_agent" '
                      'Upstream: $upstream_addr';

    access_log /var/log/nginx/access.log custom;

    upstream fastapi_app {{
        {'\n        '.join([f'server {ip}:8000;' for ip in slave_ips])}
    }}

    server {{
        listen 80;

        location / {{
            proxy_pass http://fastapi_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            add_header X-Backend-Server $upstream_addr;
        }}
    }}
}}
"""

# Subir y mover el archivo de configuración
sftp_client = ssh_client.open_sftp()
with sftp_client.open('/home/ec2-user/nginx.conf', 'w') as conf_file:
    conf_file.write(nginx_config)
sftp_client.close()

# Ejecutar comandos remotos para activar la nueva configuración
commands = [
    "sudo mv /home/ec2-user/nginx.conf /etc/nginx/nginx.conf",
    "sudo systemctl restart nginx"
]

for cmd in commands:
    stdin, stdout, stderr = ssh_client.exec_command(cmd)
    print(stdout.read().decode(), stderr.read().decode())  # Salida de depuración

# Cerrar conexión SSH
ssh_client.close()

print("Configuración de NGINX actualizada con éxito.")
