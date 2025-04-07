import boto3
import paramiko

# Crear una sesión de boto3
ec2_client = boto3.client('ec2', region_name='us-east-2')
slave_ip = '18.222.112.38'

# Configurar la conexión SSH
key_path = 'id_rsa'
key = paramiko.RSAKey.from_private_key_file(key_path)
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Conectar a la instancia 'master' via SSH
ssh_client.connect(slave_ip, username='ec2-user', pkey=key)

# Crear un Dockerfile
dockerfile_content = """
FROM pytorch/pytorch

WORKDIR /app
COPY main.py /app/main.py
COPY best_mnist_model.pth /app/best_mnist_model.pth

RUN pip install fastapi uvicorn pillow

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

# Escribir el Dockerfile
sftp_client = ssh_client.open_sftp()
with sftp_client.open('/home/ec2-user/Dockerfile', 'w') as dockerfile:
    dockerfile.write(dockerfile_content)

# Cerrar la conexión SSH
sftp_client.close()
ssh_client.close()