import boto3
import paramiko

# Crear una sesión de boto3
ec2_client = boto3.client('ec2', region_name='us-east-2')
slave_ip = "18.222.112.38" 

# Configurar la conexión SSH
key_path = 'id_rsa'
key = paramiko.RSAKey.from_private_key_file(key_path)
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Conectar a la instancia 'master' via SSH
ssh_client.connect(slave_ip, username='ec2-user', pkey=key)

# Ejecutar los comandos para construir y correr el contenedor Docker
commands = [
    'docker build -t fastapi_app .',
    'docker run -d -p 8000:8000 fastapi_app'
]

for command in commands:
    stdin, stdout, stderr = ssh_client.exec_command(command)
    print(stdout.read().decode(), stderr.read().decode())

# Cerrar la conexión SSH
ssh_client.close()