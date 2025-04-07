import boto3
import paramiko
from scp import SCPClient

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

# Subir los archivos
scp_client = SCPClient(ssh_client.get_transport())
scp_client.put('main.py', '/home/ec2-user/main.py')
scp_client.put('best_mnist_model.pth', '/home/ec2-user/best_mnist_model.pth')

# Cerrar la conexión SSH
scp_client.close()
ssh_client.close()