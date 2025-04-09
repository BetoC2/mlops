import boto3
import paramiko
# Crear una sesión de boto3
ec2_client = boto3.client('ec2', region_name='us-east-2')

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

# Ejecutar los comandos para instalar NGINX (Master)
commands = [
'sudo yum update -y',
'sudo yum install nginx -y',
'sudo systemctl start nginx',
'sudo systemctl enable nginx'
]
for command in commands:
    stdin, stdout, stderr = ssh_client.exec_command(command)
    print(stdout.read().decode(), stderr.read().decode())
# Cerrar la conexión SSH
ssh_client.close()
