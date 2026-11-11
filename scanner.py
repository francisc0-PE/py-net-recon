import argparse
import socket
from concurrent.futures import ThreadPoolExecutor
import time
from datetime import datetime

# Colores ANSI para la terminal (Estilo Hacker Pro)
VERDE = "\033[92m"
ROJO = "\033[91m"
AMARILLO = "\033[93m"
RESET = "\033[0m"

def parse_ports(port_arg: str) -> list:
    """
    Parsea los puertos ingresados por argumento.
    Soporta rangos (ej. 1-1024) o listas separadas por comas (ej. 80,443,8080).
    """
    ports = []
    try:
        if "-" in port_arg:
            start, end = map(int, port_arg.split("-"))
            ports = list(range(start, end + 1))
        elif "," in port_arg:
            ports = [int(p.strip()) for p in port_arg.split(",")]
        else:
            ports = [int(port_arg)]
    except ValueError:
        print(f"{ROJO}[-] Formato de puertos inválido. Usando puertos por defecto (80, 443).{RESET}")
        ports = [80, 443]
    return ports

def get_banner(ip: str, port: int) -> str:
    """Intenta extraer la firma o banner del servicio activo."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1.5)
            s.connect((ip, port))
            if port in [80, 8080]:
                s.send(b"HEAD / HTTP/1.1\r\nHost: " + ip.encode() + b"\r\n\r\n")
            
            banner = s.recv(1024).decode('utf-8', errors='ignore').strip()
            return banner.split('\n')[0] if banner else "Sin banner visible"
    except:
        return "Sin banner visible"

def scan_port(ip: str, port: int):
    """Escanea un puerto y solo imprime/retorna si está abierto."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1.0)
            result = s.connect_ex((ip, port))
            
            if result == 0:
                banner = get_banner(ip, port)
                mensaje = f"[+] Puerto {port} ABIERTO | Servicio: {banner}"
                print(f"{VERDE}{mensaje}{RESET}")
                return mensaje
    except:
        pass
    return None

def main():
    parser = argparse.ArgumentParser(description="PY-NET-RECON | Escáner de Superficie de Ataque Avanzado")
    parser.add_argument("-t", "--target", required=True, help="IP o Dominio objetivo (ej. scanme.nmap.org)")
    parser.add_argument("-p", "--ports", default="21,22,80,443,445,8080", help="Puertos a escanear: rango (1-1024) o lista (80,443)")
    parser.add_argument("-w", "--workers", type=int, default=50, help="Número de hilos simultáneos (Por defecto: 50)")
    
    args = parser.parse_args()

    print(f"{AMARILLO}=== PY-NET-RECON v1.2 | Dynamic Motor ==={RESET}\n")
    target_host = args.target
    
    try:
        target_ip = socket.gethostbyname(target_host)
    except socket.gaierror:
        print(f"{ROJO}[-] No se pudo resolver el host: {target_host}{RESET}")
        return

    ports_to_scan = parse_ports(args.ports)
    print(f"{AMARILLO}[*] Iniciando escaneo en {target_host} ({target_ip}) | Puertos a evaluar: {len(ports_to_scan)} | Hilos: {args.workers}{RESET}")
    start_time = time.time()
    
    resultados_totales = []
    resultados_totales.append(f"Reporte de Escaneo - Objetivo: {target_host} ({target_ip}) - Fecha: {datetime.now()}")
    resultados_totales.append(f"Rango/Puertos evaluados: {args.ports} | Hilos: {args.workers}")
    resultados_totales.append("-" * 60)

    # Escaneo multihilo masivo con ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(scan_port, target_ip, port) for port in ports_to_scan]
        for future in futures:
            res = future.result()
            if res:
                resultados_totales.append(res)

    tiempo_total = round(time.time() - start_time, 2)
    print(f"\n{AMARILLO}[*] Escaneo finalizado en {tiempo_total} segundos.{RESET}")
    resultados_totales.append(f"\nEscaneo finalizado en {tiempo_total} segundos.")

    # Guardar reporte limpio en disco
    nombre_archivo = f"reporte_{target_host.replace('.', '_')}.txt"
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write("\n".join(resultados_totales))
    
    print(f"{VERDE}[+] Reporte guardado exitosamente en: {nombre_archivo}{RESET}")

if __name__ == "__main__":
    main()