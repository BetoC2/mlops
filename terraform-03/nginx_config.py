import boto3
import paramiko

# Crear una sesión de boto3
ec2_client = boto3.client('ec2', region_name='us-east-2')
slave_ip = "18.222.112.38"
master_ip = "3.145.12.129"

# Configurar la conexión SSH
key_path = 'id_rsa'
key = paramiko.RSAKey.from_private_key_file(key_path)
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Conectar a la instancia 'master' via SSH
ssh_client.connect(master_ip, username='ec2-user', pkey=key)

# Archivo de configuración de NGINX
nginx_config = f"""
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {{
    worker_connections 1024;
}}

http {{
    upstream fastapi_app {{
        server {slave_ip}:8000;
    }}

    server {{
        listen 80;

        location / {{
            proxy_pass http://fastapi_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }}
    }}
}}
"""

# Crear/modificar el archivo de configuración en /etc/nginx/nginx.conf
sftp_client = ssh_client.open_sftp()
with sftp_client.open('/home/ec2-user/nginx.conf', 'w') as conf_file:
    conf_file.write(nginx_config)
sftp_client.close()

# Mover el archivo de configuración a la ubicación correcta y reiniciar NGINX
commands = [
    "sudo mv /home/ec2-user/nginx.conf /etc/nginx/nginx.conf",
    "sudo systemctl restart nginx"
]

for cmd in commands:
    stdin, stdout, stderr = ssh_client.exec_command(cmd)
    print(stdout.read().decode(), stderr.read().decode())  # Para depuración

# Cerrar la conexión SSH
ssh_client.close()

print("Configuración de NGINX actualizada con éxito.")