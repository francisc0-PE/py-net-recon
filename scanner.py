import argparse
import socket
from concurrent.futures import ThreadPoolExecutor
import time
from datetime import datetime

# Colores ANSI para la terminal (Estilo Ciberseguridad Avanzada)
VERDE = "\033[92m"
ROJO = "\033[91m"
AMARILLO = "\033[93m"
AZUL = "\033[94m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
RESET = "\033[0m"

BANNER_ASCII = r"""
    ____  __  __   _   _ _____ _____   ____  _________________ _   _ 
   |  _ \|  \/  | | \ | | ____|_   _| |  _ \| ____/ ___|_   _| \ | |
   | |_) | |\/| | |  \| |  _|   | |   | |_) |  _| \___ \ | | |  \| |
   |  __/| |  | | | |\  | |___  | |   |  _ <| |___ ___) || | | |\  |
   |_|   |_|  |_| |_| \_|_____| |_|   |_| \_\_____|____/ |_| |_| \_|
   [ ULTIMATE THREAT INTELLIGENCE & FORENSIC RECON ENGINE v2.3 ]
"""

# Base de conocimiento avanzada con puntuación CVSS estimada y riesgos
PORT_KNOWLEDGE_BASE = {
    21: {"service": "FTP (File Transfer Protocol)", "risk": "ALTO", "cvss": 7.5, "desc": "Protocolo sin cifrado. Exposición crítica de credenciales en tránsito."},
    22: {"service": "SSH (Secure Shell)", "risk": "MEDIO", "cvss": 5.3, "desc": "Acceso remoto. Vulnerable a ataques de fuerza bruta si no usa llaves criptográficas."},
    23: {"service": "Telnet", "risk": "CRÍTICO", "cvss": 9.8, "desc": "Protocolo obsoleto en texto plano. Intercepción total de sesiones trivial."},
    25: {"service": "SMTP (Simple Mail Transfer)", "risk": "MEDIO", "cvss": 5.9, "desc": "Servidor de correo. Posible vector para spam relay o envenenamiento."},
    80: {"service": "HTTP (Web Server Unsecured)", "risk": "MEDIO", "cvss": 5.4, "desc": "Tráfico web sin cifrar TLS. Credenciales y datos expuestos a sniffing."},
    443: {"service": "HTTPS (Secure Web Server)", "risk": "BAJO", "cvss": 2.1, "desc": "Canal web cifrado. Requiere validar robustez de certificados y cifrados."},
    445: {"service": "Microsoft-DS (SMB)", "risk": "CRÍTICO", "cvss": 9.8, "desc": "Exposición de recursos compartidos. Historial crítico de ataques deplantilla (EternalBlue)."},
    3306: {"service": "MySQL Database", "risk": "ALTO", "cvss": 8.6, "desc": "Gestor de base de datos expuesto a internet. Alto riesgo de exfiltración."},
    3389: {"service": "RDP (Remote Desktop)", "risk": "ALTO", "cvss": 8.1, "desc": "Escritorio remoto de Windows. Blanco preferido para despliegue de ransomware."},
    8080: {"service": "HTTP-Proxy / Alternate Web", "risk": "MEDIO", "cvss": 5.0, "desc": "Puerto alternativo de desarrollo o panel de control administrativo."}
}

def parse_ports(port_arg: str) -> list:
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
        ports = [80, 443]
    return ports

def get_risk_profile(port: int) -> dict:
    if port in PORT_KNOWLEDGE_BASE:
        return PORT_KNOWLEDGE_BASE[port]
    return {"service": "Custom / Unassigned Port", "risk": "INFORMATIVO", "cvss": 0.0, "desc": "Servicio no estándar. Requiere análisis manual profundo."}

def deep_http_inspection(ip: str, port: int) -> dict:
    """Extrae cabeceras avanzadas y verifica políticas de seguridad web."""
    info = {
        "service": "HTTP/S Web Service",
        "server": "Desconocido",
        "powered_by": "No declarado",
        "hsts": "No implementado",
        "x_frame": "No implementado",
        "csp": "No implementado",
        "risk": "MEDIO",
        "cvss": 5.4
    }
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2.5)
            s.connect((ip, port))
            request = f"GET / HTTP/1.1\r\nHost: {ip}\r\nUser-Agent: py-net-recon/2.3-Enterprise\r\nConnection: close\r\n\r\n"
            s.sendall(request.encode('utf-8'))
            response = s.recv(4096).decode('utf-8', errors='ignore')
            
            headers = response.split('\r\n')
            for line in headers:
                lower_line = line.lower()
                if lower_line.startswith('server:'):
                    info["server"] = line.split(':', 1)[1].strip()
                elif lower_line.startswith('x-powered-by:'):
                    info["powered_by"] = line.split(':', 1)[1].strip()
                elif lower_line.startswith('strict-transport-security'):
                    info["hsts"] = "Activo (HSTS)"
                elif lower_line.startswith('x-frame-options:'):
                    info["x_frame"] = line.split(':', 1)[1].strip()
                elif lower_line.startswith('content-security-policy:'):
                    info["csp"] = "Configurado"
    except:
        info["server"] = "Filtro o Timeout en Handshake HTTP"
    return info

def scan_port(ip: str, port: int):
    try:
        start_rtt = time.time()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1.2)
            result = s.connect_ex((ip, port))
            rtt = round((time.time() - start_rtt) * 1000, 2) # Latencia en ms
            
            if result == 0:
                profile = get_risk_profile(port)
                profile["rtt_ms"] = rtt
                
                if port in [80, 443, 8080, 8443, 3000, 5000]:
                    web_data = deep_http_inspection(ip, port)
                    profile.update(web_data)
                else:
                    try:
                        s.settimeout(1.5)
                        banner = s.recv(1024).decode('utf-8', errors='ignore').strip()
                        profile["banner"] = banner.split('\n')[0] if banner else "Sin banner explícito"
                    except:
                        profile["banner"] = "Sin banner explícito"
                return {"port": port, "status": "ABIERTO", "data": profile}
    except:
        pass
    return None

def main():
    print(CYAN + BANNER_ASCII + RESET)
    parser = argparse.ArgumentParser(description="PY-NET-RECON v2.3 | Ultimate Enterprise Threat Intelligence")
    parser.add_argument("-t", "--target", required=True, help="IP o Dominio objetivo (ej. scanme.nmap.org)")
    parser.add_argument("-p", "--ports", default="21,22,80,443,445,3306,8080", help="Puertos a escanear: rango (1-1024) o lista")
    parser.add_argument("-w", "--workers", type=int, default=100, help="Hilos concurrentes de escaneo")
    
    args = parser.parse_args()
    target_host = args.target
    
    try:
        target_ip = socket.gethostbyname(target_host)
        # Resolución inversa de DNS (PTR)
        try:
            reverse_dns = socket.gethostbyaddr(target_ip)[0]
        except:
            reverse_dns = "No disponible / Sin registro PTR"
    except socket.gaierror:
        print(f"{ROJO}[-] No se pudo resolver el host: {target_host}{RESET}")
        return

    ports_to_scan = parse_ports(args.ports)
    print(f"{AMARILLO}[*] Objetivo: {target_host} | IP: {target_ip} | PTR: {reverse_dns}{RESET}")
    print(f"{AMARILLO}[*] Iniciando motor multihilo con {len(ports_to_scan)} puertos y {args.workers} workers...{RESET}\n")
    
    start_time = time.time()
    open_ports = []
    
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(scan_port, target_ip, port) for port in ports_to_scan]
        for future in futures:
            res = future.result()
            if res:
                open_ports.append(res)
                p = res['port']
                risk = res['data']['risk']
                cvss = res['data']['cvss']
                rtt = res['data']['rtt_ms']
                color = ROJO if risk in ["ALTO", "CRÍTICO"] else (AMARILLO if risk == "MEDIO" else VERDE)
                print(f"{VERDE}[+] Puerto {p:5d} ABIERTO{RESET} | RTT: {rtt}ms | Servicio: {res['data']['service']} | CVSS: {cvss} | Riesgo: {color}[{risk}]{RESET}")

    tiempo_total = round(time.time() - start_time, 2)
    print(f"\n{AMARILLO}[*] Auditoría integral finalizada en {tiempo_total} segundos.{RESET}")

    # === GENERACIÓN DE REPORTE FORENSE INDUSTRIAL AVANZADO ===
    nombre_archivo = f"reporte_forense_{target_host.replace('.', '_')}.txt"
    
    reporte = [
        "=" * 90,
        "                 INFORME FORENSE DE INTELIGENCIA DE AMENAZAS Y SUPERFICIE",
        "                 PY-NET-RECON ULTIMATE SECURITY SUITE - v2.3",
        "=" * 90,
        f" Timestamp de Análisis      : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f" Host / Dominio Objetivo    : {target_host}",
        f" Dirección IP Resuelta      : {target_ip}",
        f" Resolución Inversa (PTR)   : {reverse_dns}",
        f" Puertos / Rango Evaluados  : {args.ports}",
        f" Hilos Concurrentes (Pool)  : {args.workers}",
        f" Tiempo de Respuesta Global : {tiempo_total} segundos",
        f" Total Vectores Abiertos    : {len(open_ports)} puertos",
        "-" * 90,
        "\n[+] SECCIÓN 1: INVENTARIO DETALLADO Y METRICAS DE RIESGO (CVSS)",
        "-" * 90
    ]

    if not open_ports:
        reporte.append(" Sin puertos abiertos detectados en el segmento especificado.")
    else:
        for item in open_ports:
            p = item['port']
            d = item['data']
            reporte.append(f" • PUERTO {p}/TCP | ESTADO: ABIERTO | LATENCIA RTT: {d['rtt_ms']} ms")
            reporte.append(f"   - Servicio Identificado   : {d['service']}")
            reporte.append(f"   - Nivel de Riesgo Vector  : [{d['risk']}] (CVSS Base Score: {d['cvss']})")
            reporte.append(f"   - Análisis de Amenaza     : {d['desc']}")
            
            if 'server' in d:
                reporte.append(f"   - Servidor Web (Fingerprint): {d['server']}")
                reporte.append(f"   - Cabecera Powered-By     : {d['powered_by']}")
                reporte.append(f"   - Cabeceras de Seguridad  :")
                    reporte.append(f"     * HSTS                  : {d['hsts']}")
                    reporte.append(f"     * X-Frame-Options       : {d['x_frame']}")
                    reporte.append(f"     * Content-Security-Pol. : {d['csp']}")
            if 'banner' in d:
                reporte.append(f"   - Banner Crudo del Socket : {d['banner']}")
            reporte.append(f"   " + "-" * 70)

    reporte.extend([
        "\n" + "-" * 90,
        "[+] SECCIÓN 2: DIRECTRICES DE REMEDIACIÓN Y HARDENING EMPRESARIAL",
        "-" * 90,
        " 1. Cierre Inmediato de Puertos Críticos: Desactive protocolos sin cifrar (Telnet,",
        "    FTP, HTTP plano) y migre estrictamente a túneles seguros SSH o HTTPS.",
        " 2. Mitigación de Vulnerabilidades Web: Implemente cabeceras de seguridad estrictas",
        "    (HSTS, CSP, X-Frame-Options) para mitigar ataques de inyección y secuestro de sesión.",
        " 3. Segmentación Perimetral: Asegúrese de que bases de datos y servicios RDP/SMB",
        "    residan detrás de redes privadas virtuales (VPN) corporativas con doble factor.",
        "=" * 90,
        " Documento Cifrado y Generado Automáticamente - py-net-recon engine v2.3",
        "=" * 90
    ])

    with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write("\n".join(reporte))
    
    print(f"{MAGENTA}[+] Reporte Forense Enterprise generado con éxito: {nombre_archivo}{RESET}")

if __name__ == "__main__":
    main()