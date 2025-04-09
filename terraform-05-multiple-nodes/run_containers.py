import boto3
import paramiko
import concurrent.futures

# Crear una sesión de boto3 (puedes usarla para otras operaciones si lo requieres)
ec2_client = boto3.client('ec2', region_name='us-east-2')

def configure_slave(ip, key_path='id_rsa', username='ec2-user'):
    try:
        # Cargar la clave privada desde el archivo
        key = paramiko.RSAKey.from_private_key_file(key_path)
        # Configurar el cliente SSH
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print(f"[{ip}] Conectando vía SSH...")
        ssh_client.connect(ip, username=username, pkey=key)
        
        # Lista de comandos a ejecutar en la instancia
        commands = [
            'docker pull albertor1/mlops:1',
            'docker run -d -p 8000:8000 albertor1/mlops:1'
        ]
        
        for command in commands:
            print(f"[{ip}] Ejecutando: {command}")
            stdin, stdout, stderr = ssh_client.exec_command(command)
            out = stdout.read().decode()
            err = stderr.read().decode()
            if out:
                print(f"[{ip}] Salida:\n{out}")
            if err:
                print(f"[{ip}] Error:\n{err}")
        
        ssh_client.close()
        print(f"[{ip}] Conexión cerrada.")
    except Exception as e:
        print(f"[{ip}] Error conectando o ejecutando comandos: {e}")

def main():
    # Leer las IPs de los slaves desde el archivo "slaves_ip.txt"
    try:
        with open('slaves_ip.txt', 'r') as f:
            slave_ips = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error al leer 'slaves_ip.txt': {e}")
        return

    print("IPs de slaves encontradas:", slave_ips)
    
    # Ejecutar la configuración en paralelo para cada slave
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(slave_ips)) as executor:
        futures = {executor.submit(configure_slave, ip): ip for ip in slave_ips}
        for future in concurrent.futures.as_completed(futures):
            ip = futures[future]
            try:
                future.result()
            except Exception as exc:
                print(f"[{ip}] Error en la ejecución paralela: {exc}")

if __name__ == "__main__":
    main()
