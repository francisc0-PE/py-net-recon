<a id="top"></a>

<div align="center">

# 🛰️🔍 PY-NET-RECON 🔍🛰️

### ⚡ v2.3 Ultimate Enterprise Threat Intelligence & Forensic Recon Engine ⚡

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![Dependencies](https://img.shields.io/badge/Dependencies-0-brightgreen)
![Version](https://img.shields.io/badge/Version-2.3-blue)
![Use](https://img.shields.io/badge/Use-Ethical%20Hacking-red)
![Languages](https://img.shields.io/badge/Docs-EN%20%7C%20ES%20%7C%20FR%20%7C%20中文-orange)

**🕵️ Discover · 🧠 Analyze · 🛡️ Protect**

---

### 🌍 Language / Idioma / Langue / 语言

[🇬🇧 **English**](#en) &nbsp;│&nbsp; [🇪🇸 **Español**](#es) &nbsp;│&nbsp; [🇫🇷 **Français**](#fr) &nbsp;│&nbsp; [🇨🇳 **中文**](#zh)

</div>

---
---

<a id="en"></a>

<div align="center">

# 🇬🇧 ENGLISH

[🏠 Top](#top) · [🇪🇸 ES](#es) · [🇫🇷 FR](#fr) · [🇨🇳 中文](#zh)

</div>

**📑 Contents:** [Overview](#en-overview) · [Features](#en-features) · [Requirements](#en-requirements) · [Installation](#en-install) · [Usage](#en-usage) · [Architecture](#en-arch) · [Disclaimer](#en-disclaimer) · [Author](#en-author)

<a id="en-overview"></a>

## 🎯 Overview

**py-net-recon** is a **network reconnaissance** tool written in Python. It finds which **TCP ports are open** on a target, identifies **which service (and version) answers** behind each one, and saves everything in a timestamped report.

### 🧭 Why it matters in Phase 1 of a Pentest / Red Team engagement

Every authorized intrusion starts with **Reconnaissance & Enumeration**. Before anything can be assessed, you must know:

| ❓ Question | 🛠️ How py-net-recon answers it |
|---|---|
| Who is the target and what is its IP? | Forward DNS plus reverse DNS (PTR) |
| Which doors are open? | TCP *connect* scan |
| How responsive is each open port? | Socket connection RTT in milliseconds |
| What web defenses are visible? | HTTP security-header inspection |
| How should findings be prioritized? | Estimated CVSS score and risk tier |
| How do I keep evidence? | Structured forensic `.txt` report |

> 💡 **Attack surface** = every exposed entry point. What you can't see, you can't defend (or audit).

<a id="en-features"></a>

## 🚀 Main Features

### 1️⃣ 🔌 TCP scanning with sockets and clean connection closing
Uses `socket` with `AF_INET` + `SOCK_STREAM` (TCP/IPv4) and `connect_ex()`, which **returns an error code instead of raising an exception**: `0` means the **port is open**.
- ⏱️ **1.2 s** connection timeout per port, so filtered ports do not stall the scan indefinitely.
- 🧹 `with socket.socket(...)` closes the connection **even if an error occurs**, preventing descriptor leaks.

### 2️⃣ ⚡ Massive multithreading with `ThreadPoolExecutor`
Port scanning is **I/O-bound**: the program mostly *waits* for the network. A thread pool waits on dozens of connections **at the same time**.
- 🧵 Configurable concurrency (`-w`, default 100).
- 📈 Scanning ports 1-1024 drops from minutes (sequential) to seconds.
- 🔒 The `with ThreadPoolExecutor` block guarantees every thread finishes and is released.

### 3️⃣ 🏷️ Banner Grabbing (service signatures & versions)
When a port is open, a new connection is made and the service's first reply is read:

| Port | Typical service | Technique |
|:---:|---|---|
| **22** | SSH | Server announces itself: `SSH-2.0-OpenSSH_8.9...` |
| **80 / 8080** | HTTP | Sends `GET / HTTP/1.1` + `Host` for web inspection |
| **21 / others** | FTP, etc. | Reads the greeting message |

Only the **first line** is kept, decoded with `errors='ignore'`. No reply → `Sin banner visible` (no visible banner).

### 4️⃣ 🖥️ Professional CLI with `argparse`
Automatic help (`-h`), required arguments and typed values (`-w` is an integer). Output uses **ANSI colors**: 🟢 open, 🟡 info, 🔴 errors.

### 5️⃣ 🎛️ Dynamic port-range engine
`parse_ports()` understands three formats:

| Format | Example | Result |
|---|---|---|
| 📏 Range | `1-1024` | Ports 1 to 1024 (inclusive) |
| 📝 List | `22,80,443` | Only those ports |
| 🎯 Single | `8080` | One port |

Invalid input never crashes the tool: it warns and falls back to `80, 443`.

### 6️⃣ 🗂️ Automatic forensic `.txt` reports with timestamps
Each run writes `reporte_forense_<target>.txt` (dots replaced by `_`) with the target, resolved IP, **exact analysis timestamp**, selected ports, worker count, total duration, open-port inventory, and per-port findings. The report is structured for review and is overwritten when the same target is scanned again.

### 7️⃣ 🔁 Reverse DNS (PTR) resolution
After resolving a hostname to IPv4, the scanner performs a reverse lookup with `gethostbyaddr()` and displays the associated PTR hostname in the console and report. If no PTR record is available, the report records that explicitly; reverse DNS is an observation, not proof of asset ownership.

### 8️⃣ ⏱️ Per-port socket response time (RTT)
The scanner measures elapsed time around each TCP `connect_ex()` attempt and expresses it in milliseconds. RTT is displayed and retained in the report for **open ports**; closed or unreachable attempts are not included in the findings inventory. This is connection-establishment timing, not a continuous latency test.

### 9️⃣ 🛡️ Web security-header inspection
For selected web ports (`80`, `443`, `8080`, `8443`, `3000`, `5000`), the scanner requests the root page and inspects `Strict-Transport-Security` (HSTS), `X-Frame-Options`, `Content-Security-Policy`, and `X-Powered-By`; it also records the `Server` banner. Missing or undisclosed headers are shown as such, not treated as proof of a vulnerability.

> ⚠️ Inspection sends plain HTTP and does not negotiate TLS. HTTPS-only services may therefore return incomplete or unavailable header data; verify them with a TLS-capable web assessment.

### 🔟 📊 Risk matrix and estimated CVSS
Known ports are mapped to a service profile, one of four severity categories (low, medium, high, or critical; displayed by the CLI as `BAJO`, `MEDIO`, `ALTO`, or `CRÍTICO`), and a numeric **estimated CVSS base score**. Unmapped ports are marked `INFORMATIVO` with a score of `0.0`.

> ℹ️ These are heuristic port-level estimates, not CVSS assessments of confirmed vulnerabilities, CVE matches, or exploitability. Validate each finding in context before making a risk decision.

### 1️⃣1️⃣ 🧾 Industrial forensic reporting and hardening guidance
The generated report includes an analysis summary, target and PTR identity, scan scope and timing, open-port/service inventory, RTT and risk metrics, available web-header observations, and a remediation/hardening section. Recommendations cover insecure protocols, web security headers, and network segmentation for sensitive services.

<a id="en-requirements"></a>

## 📦 Requirements & Dependencies

| Requirement | Detail |
|---|---|
| 🐍 **Python** | 3.8 or higher |
| 📚 **External dependencies** | **None** ✅ |
| 💻 **OS** | Windows, Linux, macOS |

**100% Python standard library**: `argparse`, `socket`, `concurrent.futures`, `time`, `datetime`. ✨ No `pip install`, easy to audit, portable, and ideal for learning how a scanner really works under the hood.

<a id="en-install"></a>

## 🛠️ Installation

```bash
# 1️⃣ Check Python
python --version        # on Linux/macOS: python3 --version

# 2️⃣ Clone the repository
git clone https://github.com/francisc0-PE/py-net-recon.git
cd py-net-recon

# 3️⃣ Verify it works
python scanner.py --help
```

🎉 That's it. Nothing else to install.

<a id="en-usage"></a>

## 🎮 Usage & Practical Examples

| Flag | Long | Required | Description | Default |
|:---:|---|:---:|---|---|
| `-t` | `--target` | ✅ | Target IP or domain | — |
| `-p` | `--ports` | ❌ | Range (`1-1024`) or list (`80,443`) | `21,22,80,443,445,3306,8080` |
| `-w` | `--workers` | ❌ | Simultaneous threads | `100` |
| `-h` | `--help` | ❌ | Show help | — |

```bash
# 📖 Help
python scanner.py --help

# 🔹 Quick scan with default ports
python scanner.py -t scanme.nmap.org

# 🔹 Well-known ports range
python scanner.py -t scanme.nmap.org -p 1-1024

# 🔹 Specific port list
python scanner.py -t 192.168.1.10 -p 22,80,443,3306,8080

# 🔹 Maximum speed with 200 threads
python scanner.py -t scanme.nmap.org -p 1-5000 -w 200
```

📺 **Sample output** (illustrative):

```text
=== PY-NET-RECON v2.3 | Ultimate Threat Intelligence & Forensic Recon Engine ===

[*] Objetivo: scanme.nmap.org | IP: 45.33.32.156 | PTR: scanme.nmap.org
[*] Iniciando motor multihilo con 7 puertos y 100 workers...
[+] Puerto    22 ABIERTO | RTT: 12.34ms | Servicio: SSH (Secure Shell) | CVSS: 5.3 | Riesgo: [MEDIO]

[*] Auditoría integral finalizada en 0.42 segundos.
[+] Reporte Forense Enterprise generado con éxito: reporte_forense_scanme_nmap_org.txt
```

> 🧪 Practice legally with `scanme.nmap.org` (allowed by the Nmap project, moderate use) or your own lab.
> ⚙️ More threads = more speed, but also more noise and risk of saturating your network or triggering an IDS/firewall.

<a id="en-arch"></a>

## 🧠 Code Architecture & Pedagogical Walkthrough

Everything lives in [scanner.py](scanner.py), split into **small single-purpose functions**.

```text
 CLI (argparse)
     │   -t target   -p ports   -w threads
     ▼
 gethostbyname()  ──► target IPv4 ──► gethostbyaddr() ──► PTR
     ▼
 parse_ports()    ──► [21, 22, 80, ...]
     ▼
 ThreadPoolExecutor (N threads)
     ├─► scan_port(ip, 21)  ┐
     ├─► scan_port(ip, 80)  ├─ connect_ex + RTT ─► risk profile / web inspection
     └─► scan_port(ip, ...) ┘
     ▼
 future.result() ──► list of open-port results
     ▼
 reporte_forense_<target>.txt ──► inventory + risk + remediation
```

| Function | Role | Technical detail |
|---|---|---|
| `parse_ports()` | 🎛️ Port engine | Text → `list[int]`; safe fallback to 80, 443 |
| `get_risk_profile()` | 📊 Risk mapping | Known-port service, tier and estimated CVSS profile |
| `deep_http_inspection()` | 🛡️ Web inspection | Reads selected HTTP response headers and server metadata |
| `scan_port()` | 🔌 Unit of work | TCP connect, RTT measurement, banner/risk and optional web inspection |
| `main()` | 🎼 Orchestrator | CLI, forward/reverse DNS, thread pool, output and forensic report |

### 🧵 How do the threads flow?
1. `main()` creates the pool with `max_workers = -w`.
2. `executor.submit()` queues **one task per port** and returns a `Future`.
3. Idle threads pull tasks from the queue; each opens **its own socket** (no shared state → no race conditions in the scan itself).
4. `future.result()` blocks until each task ends and collects its return value (`str` or `None`).
5. Leaving the `with` block shuts the pool down cleanly.

### 🎓 What you will learn
TCP sockets and the implicit three-way handshake in `connect_ex`; concurrency for I/O-bound work; safe resource handling with context managers; CLI design with `argparse` and tolerance to bad input.

### 🔭 Known limitations & roadmap
TCP/IPv4 *connect* scan only · RTT is reported for open ports · CVSS values are heuristic port profiles, not vulnerability verification · web inspection uses plain HTTP without TLS negotiation · reports are plain text and overwritten for a repeated target · no authenticated testing, exploit validation, or CVE correlation.

<a id="en-disclaimer"></a>

## ⚖️ Ethical Disclaimer

> ### 🚨 LEGAL AND AUTHORIZED USE ONLY 🚨

This tool is provided **exclusively** for:
- ✅ **Ethical hacking** and penetration testing **with written authorization**.
- ✅ **Audits** of systems and networks **you own** or are contracted to assess.
- ✅ **Education** and research in controlled labs.

❌ **Scanning systems without explicit permission is prohibited** and may constitute a **computer crime** under your local law. The author accepts **no liability** for misuse or resulting damage. **You alone are responsible for your actions.** 🛡️

<a id="en-author"></a>

## 👨‍💻 Author & Vision

**Created by:** [@francisc0-PE](https://github.com/francisc0-PE)

🌟 py-net-recon exists to **prove that real cybersecurity tooling can be built in pure Python** while understanding every piece, from the socket to the report. The goal: grow step by step into a modular, educational and professional reconnaissance toolkit. 🤝 Issues and pull requests are welcome, and a ⭐ is appreciated!

<div align="right">

[⬆️ Back to top](#top)

</div>

---
---

<a id="es"></a>

<div align="center">

# 🇪🇸 ESPAÑOL

[🏠 Inicio](#top) · [🇬🇧 EN](#en) · [🇫🇷 FR](#fr) · [🇨🇳 中文](#zh)

</div>

**📑 Contenido:** [Descripción](#es-overview) · [Características](#es-features) · [Requisitos](#es-requirements) · [Instalación](#es-install) · [Uso](#es-usage) · [Arquitectura](#es-arch) · [Descargo](#es-disclaimer) · [Autor](#es-author)

<a id="es-overview"></a>

## 🎯 Descripción general

**py-net-recon** es una herramienta de **reconocimiento de red** escrita en Python. Identifica qué **puertos TCP están abiertos** en un objetivo, qué **servicio (y versión) responde** detrás de cada uno, y guarda todo en un reporte con marca de tiempo.

### 🧭 ¿Por qué es clave en la Fase 1 de un Pentest / Red Team?

Toda intrusión autorizada comienza con **Reconocimiento y Enumeración**. Antes de evaluar nada, debes saber:

| ❓ Pregunta | 🛠️ Cómo la responde py-net-recon |
|---|---|
| ¿Quién es el objetivo y cuál es su IP? | DNS directo e inverso (PTR) |
| ¿Qué puertas están abiertas? | Escaneo TCP *connect* |
| ¿Qué capacidad de respuesta tiene cada puerto abierto? | RTT de conexión TCP en milisegundos |
| ¿Qué defensas web están visibles? | Inspección de cabeceras HTTP |
| ¿Cómo priorizo los hallazgos? | CVSS estimado y nivel de riesgo |
| ¿Cómo conservo la evidencia? | Reporte forense `.txt` estructurado |

> 💡 **Superficie de ataque** = todos los puntos de entrada expuestos. Lo que no conoces, no lo puedes defender (ni auditar).

<a id="es-features"></a>

## 🚀 Características principales

### 1️⃣ 🔌 Escaneo TCP con Sockets y cierre de conexiones
Usa `socket` con `AF_INET` + `SOCK_STREAM` (TCP/IPv4) y `connect_ex()`, que **devuelve un código de error en vez de lanzar excepción**: `0` significa **puerto abierto**.
- ⏱️ *Timeout* de conexión de **1.2 s** por puerto: los puertos filtrados no bloquean indefinidamente el escaneo.
- 🧹 `with socket.socket(...)` **cierra siempre la conexión**, incluso ante errores, evitando fugas de descriptores.

### 2️⃣ ⚡ Multithreading masivo con `ThreadPoolExecutor`
Escanear puertos es una tarea **limitada por E/S (I/O-bound)**: el programa pasa casi todo el tiempo *esperando* a la red. Un *pool* de hilos espera decenas de conexiones **a la vez**.
- 🧵 Concurrencia configurable (`-w`, por defecto 100).
- 📈 Escanear 1-1024 pasa de minutos (secuencial) a segundos.
- 🔒 El bloque `with ThreadPoolExecutor` garantiza que todos los hilos terminen y se liberen.

### 3️⃣ 🏷️ Banner Grabbing (firmas y versiones de servicios)
Con un puerto abierto, se abre una nueva conexión y se lee la primera respuesta del servicio:

| Puerto | Servicio típico | Técnica |
|:---:|---|---|
| **22** | SSH | El servidor se anuncia: `SSH-2.0-OpenSSH_8.9...` |
| **80 / 8080** | HTTP | Envía `GET / HTTP/1.1` + `Host` para inspeccionar el servicio web |
| **21 / otros** | FTP, etc. | Lee el mensaje de bienvenida |

Solo se conserva la **primera línea**, decodificada con `errors='ignore'`. Sin respuesta → `Sin banner visible`.

### 4️⃣ 🖥️ CLI profesional con `argparse`
Ayuda automática (`-h`), argumentos obligatorios y tipos validados (`-w` es entero). Salida con **colores ANSI**: 🟢 abiertos, 🟡 información, 🔴 errores.

### 5️⃣ 🎛️ Motor de rangos dinámicos de puertos
`parse_ports()` interpreta tres formatos:

| Formato | Ejemplo | Resultado |
|---|---|---|
| 📏 Rango | `1-1024` | Del 1 al 1024 (inclusive) |
| 📝 Lista | `22,80,443` | Solo esos puertos |
| 🎯 Único | `8080` | Un solo puerto |

Una entrada inválida no rompe la herramienta: avisa y usa `80, 443`.

### 6️⃣ 🗂️ Reportes forenses `.txt` con marcas de tiempo
Cada ejecución genera `reporte_forense_<objetivo>.txt` (puntos reemplazados por `_`) con objetivo, IP resuelta, **fecha/hora exacta**, puertos seleccionados, número de hilos, duración total e inventario detallado de puertos abiertos. El archivo se sobrescribe al repetir el escaneo del mismo objetivo.

### 7️⃣ 🔁 Resolución inversa de DNS (PTR)
Tras resolver el dominio a IPv4, se consulta `gethostbyaddr()` para identificar el nombre PTR asociado a la IP. El valor se muestra en consola y se incluye en el reporte; si no existe un registro PTR, se indica expresamente. No constituye una verificación de propiedad del activo.

### 8️⃣ ⏱️ Tiempo de respuesta por socket (RTT)
Se mide en milisegundos el tiempo transcurrido alrededor de cada intento TCP con `connect_ex()`. El RTT se muestra y conserva en el informe para los **puertos abiertos**; los intentos cerrados o inalcanzables no se incluyen en el inventario de hallazgos. Es una medición de establecimiento de conexión, no una prueba continua de latencia.

### 9️⃣ 🛡️ Inspección de cabeceras de seguridad web
En puertos web seleccionados (`80`, `443`, `8080`, `8443`, `3000`, `5000`), se solicita la página raíz y se inspeccionan `Strict-Transport-Security` (HSTS), `X-Frame-Options`, `Content-Security-Policy` y `X-Powered-By`; también se registra la cabecera `Server`. Una cabecera ausente o no declarada no demuestra por sí sola que exista una vulnerabilidad.

> ⚠️ La inspección envía HTTP sin negociar TLS. Los servicios exclusivamente HTTPS pueden devolver datos incompletos o no disponibles; verifícalos con una evaluación web compatible con TLS.

### 🔟 📊 Matriz de riesgo y CVSS estimado
Los puertos conocidos se asocian a un perfil de servicio, una de cuatro categorías de severidad (bajo, medio, alto o crítico; la CLI las muestra como `BAJO`, `MEDIO`, `ALTO` o `CRÍTICO`) y una **puntuación base CVSS estimada**. Los puertos sin perfil se marcan `INFORMATIVO` con puntuación `0.0`.

> ℹ️ Son estimaciones heurísticas por puerto, no evaluaciones CVSS de vulnerabilidades confirmadas, coincidencias CVE ni mediciones de explotabilidad. Valida cada hallazgo antes de decidir su riesgo.

### 1️⃣1️⃣ 🧾 Informes forenses industriales y guía de hardening
El informe generado reúne el resumen del análisis, identidad del objetivo y PTR, alcance y tiempos del escaneo, inventario de puertos/servicios abiertos, RTT y métricas de riesgo, observaciones de cabeceras web disponibles y una sección de remediación y hardening. Incluye recomendaciones sobre protocolos inseguros, cabeceras web defensivas y segmentación de servicios sensibles.

<a id="es-requirements"></a>

## 📦 Requisitos previos y dependencias

| Requisito | Detalle |
|---|---|
| 🐍 **Python** | 3.8 o superior |
| 📚 **Dependencias externas** | **Ninguna** ✅ |
| 💻 **SO** | Windows, Linux, macOS |

**100 % librería estándar**: `argparse`, `socket`, `concurrent.futures`, `time`, `datetime`. ✨ Sin `pip install`, fácil de auditar, portable e ideal para aprender cómo funciona un escáner *por debajo*.

<a id="es-install"></a>

## 🛠️ Guía de instalación

```bash
# 1️⃣ Verifica Python
python --version        # en Linux/macOS: python3 --version

# 2️⃣ Clona el repositorio
git clone https://github.com/francisc0-PE/py-net-recon.git
cd py-net-recon

# 3️⃣ Comprueba que funciona
python scanner.py --help
```

🎉 ¡Listo! No hay nada más que instalar.

<a id="es-usage"></a>

## 🎮 Manual de uso y ejemplos prácticos

| Flag | Largo | Obligatorio | Descripción | Por defecto |
|:---:|---|:---:|---|---|
| `-t` | `--target` | ✅ | IP o dominio objetivo | — |
| `-p` | `--ports` | ❌ | Rango (`1-1024`) o lista (`80,443`) | `21,22,80,443,445,3306,8080` |
| `-w` | `--workers` | ❌ | Hilos simultáneos | `100` |
| `-h` | `--help` | ❌ | Muestra la ayuda | — |

```bash
# 📖 Ayuda
python scanner.py --help

# 🔹 Escaneo rápido con puertos por defecto
python scanner.py -t scanme.nmap.org

# 🔹 Rango de puertos conocidos
python scanner.py -t scanme.nmap.org -p 1-1024

# 🔹 Lista de puertos específicos
python scanner.py -t 192.168.1.10 -p 22,80,443,3306,8080

# 🔹 Máxima velocidad con 200 hilos
python scanner.py -t scanme.nmap.org -p 1-5000 -w 200
```

📺 **Ejemplo de salida** (ilustrativo):

```text
=== PY-NET-RECON v2.3 | Ultimate Threat Intelligence & Forensic Recon Engine ===

[*] Objetivo: scanme.nmap.org | IP: 45.33.32.156 | PTR: scanme.nmap.org
[*] Iniciando motor multihilo con 7 puertos y 100 workers...
[+] Puerto    22 ABIERTO | RTT: 12.34ms | Servicio: SSH (Secure Shell) | CVSS: 5.3 | Riesgo: [MEDIO]

[*] Auditoría integral finalizada en 0.42 segundos.
[+] Reporte Forense Enterprise generado con éxito: reporte_forense_scanme_nmap_org.txt
```

> 🧪 Practica legalmente con `scanme.nmap.org` (permitido por el proyecto Nmap, uso moderado) o con tu propio laboratorio.
> ⚙️ Más hilos = más velocidad, pero también más ruido y riesgo de saturar tu red o activar un IDS/firewall.

<a id="es-arch"></a>

## 🧠 Arquitectura del código y explicación pedagógica

Todo vive en [scanner.py](scanner.py), organizado en **funciones pequeñas de responsabilidad única**.

```text
 CLI (argparse)
     │   -t objetivo   -p puertos   -w hilos
     ▼
 gethostbyname()  ──► IP del objetivo ──► gethostbyaddr() ──► PTR
     ▼
 parse_ports()    ──► [21, 22, 80, ...]
     ▼
 ThreadPoolExecutor (N hilos)
     ├─► scan_port(ip, 21)  ┐
     ├─► scan_port(ip, 80)  ├─ connect_ex + RTT ─► perfil de riesgo / inspección web
     └─► scan_port(ip, ...) ┘
     ▼
 future.result() ──► lista de puertos abiertos
     ▼
 reporte_forense_<objetivo>.txt ──► inventario + riesgo + remediación
```

| Función | Rol | Detalle técnico |
|---|---|---|
| `parse_ports()` | 🎛️ Motor de puertos | Texto → `list[int]`; *fallback* seguro a 80, 443 |
| `get_risk_profile()` | 📊 Matriz de riesgo | Servicio, nivel y perfil CVSS estimado por puerto conocido |
| `deep_http_inspection()` | 🛡️ Inspección web | Lee cabeceras HTTP seleccionadas y datos del servidor |
| `scan_port()` | 🔌 Unidad de trabajo | Conexión TCP, medición RTT, riesgo/banner e inspección web opcional |
| `main()` | 🎼 Orquestador | CLI, DNS directo/inverso, pool de hilos, salida e informe forense |

### 🧵 ¿Cómo fluyen los hilos?
1. `main()` crea el *pool* con `max_workers = -w`.
2. `executor.submit()` encola **una tarea por puerto** y devuelve un `Future`.
3. Los hilos libres toman tareas de la cola; cada una abre **su propio socket** (sin estado compartido → sin condiciones de carrera en el escaneo).
4. `future.result()` bloquea hasta que cada tarea termina y recoge su retorno (`str` o `None`).
5. Al salir del `with`, el pool se cierra limpiamente.

### 🎓 Qué aprenderás
Sockets TCP y el *three-way handshake* implícito en `connect_ex`; concurrencia en tareas I/O-bound; gestión segura de recursos con *context managers*; diseño de CLIs con `argparse` y tolerancia a entradas inválidas.

### 🔭 Limitaciones conocidas
Solo escaneo TCP/IPv4 de tipo *connect* · RTT incluido en los resultados de puertos abiertos · CVSS heurístico por perfil de puerto, sin validar vulnerabilidades · inspección web HTTP sin negociación TLS · informes de texto que se sobrescriben al repetir el objetivo · sin pruebas autenticadas, explotación ni correlación con CVE.

<a id="es-disclaimer"></a>

## ⚖️ Descargo de responsabilidad ético

> ### 🚨 USO EXCLUSIVAMENTE LEGAL Y AUTORIZADO 🚨

Esta herramienta se ofrece **únicamente** para:
- ✅ **Hacking ético** y pruebas de penetración **con autorización escrita**.
- ✅ **Auditorías** de sistemas y redes **de tu propiedad** o bajo contrato.
- ✅ **Educación** e investigación en laboratorios controlados.

❌ **Escanear sistemas sin permiso explícito está prohibido** y puede constituir un **delito informático** según tu legislación. El autor **no se hace responsable** del mal uso ni de los daños derivados. **Tú eres el único responsable de tus actos.** 🛡️

<a id="es-author"></a>

## 👨‍💻 Autor / Creador y visión del proyecto

**Creado por:** [@francisc0-PE](https://github.com/francisc0-PE)

🌟 py-net-recon nació para **demostrar que, con Python puro, se puede construir una herramienta de ciberseguridad real**, entendiendo cada pieza: desde el socket hasta el reporte. La meta: crecer paso a paso hacia un *toolkit* de reconocimiento modular, didáctico y profesional. 🤝 ¡*Issues* y *pull requests* son bienvenidos, y una ⭐ se agradece!

<div align="right">

[⬆️ Volver arriba](#top)

</div>

---
---

<a id="fr"></a>

<div align="center">

# 🇫🇷 FRANÇAIS

*Rédigé dans un registre technique et formel, usuel en entreprise au Grand-Duché de Luxembourg.*

[🏠 Accueil](#top) · [🇬🇧 EN](#en) · [🇪🇸 ES](#es) · [🇨🇳 中文](#zh)

</div>

**📑 Sommaire :** [Présentation](#fr-overview) · [Fonctionnalités](#fr-features) · [Prérequis](#fr-requirements) · [Installation](#fr-install) · [Utilisation](#fr-usage) · [Architecture](#fr-arch) · [Avertissement](#fr-disclaimer) · [Auteur](#fr-author)

<a id="fr-overview"></a>

## 🎯 Présentation générale

**py-net-recon** est un outil de **reconnaissance réseau** développé en Python. Il détermine quels **ports TCP sont ouverts** sur une cible, quel **service (et quelle version)** répond derrière chacun d'eux, puis consigne l'ensemble dans un rapport horodaté.

### 🧭 Pourquoi est-il essentiel en Phase 1 d'un test d'intrusion / Red Team ?

Toute intrusion autorisée débute par la **reconnaissance et l'énumération**. Avant toute évaluation, il convient de savoir :

| ❓ Question | 🛠️ Réponse apportée par py-net-recon |
|---|---|
| Quelle est la cible et son adresse IP ? | DNS direct et inverse (PTR) |
| Quelles portes sont ouvertes ? | Scan TCP de type *connect* |
| Quelle est la réactivité de chaque port ouvert ? | RTT TCP en millisecondes |
| Quelles défenses web sont visibles ? | Inspection des en-têtes HTTP |
| Comment hiérarchiser les constats ? | CVSS estimé et niveau de risque |
| Comment conserver les éléments probants ? | Rapport forensique `.txt` structuré |

> 💡 **Surface d'attaque** = ensemble des points d'entrée exposés. On ne peut ni défendre ni auditer ce que l'on ne connaît pas.

<a id="fr-features"></a>

## 🚀 Fonctionnalités principales

### 1️⃣ 🔌 Scan TCP via sockets et fermeture propre des connexions
Utilise `socket` avec `AF_INET` + `SOCK_STREAM` (TCP/IPv4) et `connect_ex()`, qui **renvoie un code d'erreur au lieu de lever une exception** : `0` signifie que le **port est ouvert**.
- ⏱️ Délai de connexion de **1,2 s** par port : les ports filtrés ne bloquent pas le scan indéfiniment.
- 🧹 `with socket.socket(...)` **ferme systématiquement la connexion**, même en cas d'erreur, ce qui évite toute fuite de descripteurs.

### 2️⃣ ⚡ Multithreading massif avec `ThreadPoolExecutor`
Le scan de ports est une tâche **liée aux E/S (I/O-bound)** : le programme passe l'essentiel de son temps à *attendre* le réseau. Un *pool* de threads attend des dizaines de connexions **simultanément**.
- 🧵 Concurrence paramétrable (`-w`, 50 par défaut).
- 📈 Le scan des ports 1 à 1024 passe de plusieurs minutes (séquentiel) à quelques secondes.
- 🔒 Le bloc `with ThreadPoolExecutor` garantit que tous les threads se terminent et sont libérés.

### 3️⃣ 🏷️ Banner Grabbing (signatures et versions des services)
Lorsqu'un port est ouvert, une nouvelle connexion est établie et la première réponse du service est lue :

| Port | Service type | Technique |
|:---:|---|---|
| **22** | SSH | Le serveur s'annonce : `SSH-2.0-OpenSSH_8.9...` |
| **80 / 8080** | HTTP | Envoi de `GET / HTTP/1.1` + `Host` pour inspecter le service web |
| **21 / autres** | FTP, etc. | Lecture du message d'accueil |

Seule la **première ligne** est conservée, décodée avec `errors='ignore'`. Sans réponse : `Sin banner visible` (aucune bannière visible).

### 4️⃣ 🖥️ Interface en ligne de commande (CLI) professionnelle avec `argparse`
Aide automatique (`-h`), arguments obligatoires et valeurs typées (`-w` est un entier). Sortie en **couleurs ANSI** : 🟢 ouverts, 🟡 informations, 🔴 erreurs.

### 5️⃣ 🎛️ Moteur de plages de ports dynamiques
`parse_ports()` interprète trois formats :

| Format | Exemple | Résultat |
|---|---|---|
| 📏 Plage | `1-1024` | Ports 1 à 1024 (inclus) |
| 📝 Liste | `22,80,443` | Uniquement ces ports |
| 🎯 Unique | `8080` | Un seul port |

Une saisie invalide ne provoque jamais de plantage : l'outil avertit l'utilisateur et applique `80, 443` par défaut.

### 6️⃣ 🗂️ Rapports forensiques `.txt` automatiques et horodatés
Chaque exécution produit `reporte_forense_<cible>.txt` (points remplacés par `_`) avec la cible, l'adresse IP résolue, l'**horodatage précis**, les ports sélectionnés, le nombre de threads, la durée totale et l'inventaire détaillé des ports ouverts. Le fichier est écrasé lors d'un nouveau scan de la même cible.

### 7️⃣ 🔁 Résolution DNS inverse (PTR)
Après la résolution du nom d'hôte en IPv4, `gethostbyaddr()` recherche le nom PTR associé à l'adresse IP. Le résultat apparaît dans la console et le rapport ; en l'absence d'enregistrement PTR, cette indisponibilité est signalée. Cette donnée ne prouve pas la propriété de l'actif.

### 8️⃣ ⏱️ Temps de réponse socket par port (RTT)
Le temps écoulé autour de chaque tentative TCP `connect_ex()` est mesuré en millisecondes. Le RTT est affiché et conservé dans le rapport pour les **ports ouverts** ; les tentatives fermées ou injoignables ne figurent pas dans l'inventaire des constats. Il s'agit du temps d'établissement de la connexion, et non d'une mesure continue de latence.

### 9️⃣ 🛡️ Inspection des en-têtes de sécurité web
Sur certains ports web (`80`, `443`, `8080`, `8443`, `3000`, `5000`), l'outil demande la page racine et examine `Strict-Transport-Security` (HSTS), `X-Frame-Options`, `Content-Security-Policy` et `X-Powered-By`; l'en-tête `Server` est également relevé. L'absence ou la non-déclaration d'un en-tête ne prouve pas à elle seule une vulnérabilité.

> ⚠️ L'inspection envoie une requête HTTP sans négociation TLS. Les services HTTPS uniquement peuvent fournir des données incomplètes ou indisponibles ; vérifiez-les avec un audit web compatible TLS.

### 🔟 📊 Matrice de risque et CVSS estimé
Les ports connus sont associés à un profil de service, à l'une des quatre catégories de gravité (faible, moyen, élevé ou critique ; libellées dans la CLI `BAJO`, `MEDIO`, `ALTO` ou `CRÍTICO`) et à un **score de base CVSS estimé**. Les ports sans profil portent le libellé `INFORMATIVO` et le score `0.0`.

> ℹ️ Il s'agit d'estimations heuristiques au niveau du port, et non d'évaluations CVSS de vulnérabilités confirmées, de correspondances CVE ou de mesures d'exploitabilité. Chaque constat doit être validé dans son contexte.

### 1️⃣1️⃣ 🧾 Rapports forensiques industriels et recommandations de durcissement
Le rapport rassemble un résumé de l'analyse, l'identité de la cible et le PTR, le périmètre et les temps du scan, l'inventaire des ports/services ouverts, les RTT et métriques de risque, les observations disponibles sur les en-têtes web, ainsi qu'une section de remédiation et de durcissement. Les recommandations portent sur les protocoles non sécurisés, les en-têtes défensifs et la segmentation des services sensibles.

<a id="fr-requirements"></a>

## 📦 Prérequis et dépendances

| Prérequis | Détail |
|---|---|
| 🐍 **Python** | 3.8 ou supérieur |
| 📚 **Dépendances externes** | **Aucune** ✅ |
| 💻 **Système** | Windows, Linux, macOS |

**100 % bibliothèque standard** : `argparse`, `socket`, `concurrent.futures`, `time`, `datetime`. ✨ Aucun `pip install`, code aisément auditable, portable, et idéal pour comprendre le fonctionnement interne d'un scanner.

<a id="fr-install"></a>

## 🛠️ Guide d'installation

```bash
# 1️⃣ Vérifier la version de Python
python --version        # sous Linux/macOS : python3 --version

# 2️⃣ Cloner le dépôt
git clone https://github.com/francisc0-PE/py-net-recon.git
cd py-net-recon

# 3️⃣ Vérifier le bon fonctionnement
python scanner.py --help
```

🎉 C'est tout : aucune autre installation n'est requise.

<a id="fr-usage"></a>

## 🎮 Mode d'emploi et exemples pratiques

| Option | Forme longue | Obligatoire | Description | Valeur par défaut |
|:---:|---|:---:|---|---|
| `-t` | `--target` | ✅ | Adresse IP ou nom de domaine de la cible | — |
| `-p` | `--ports` | ❌ | Plage (`1-1024`) ou liste (`80,443`) | `21,22,80,443,445,3306,8080` |
| `-w` | `--workers` | ❌ | Nombre de threads simultanés | `100` |
| `-h` | `--help` | ❌ | Affiche l'aide | — |

```bash
# 📖 Aide
python scanner.py --help

# 🔹 Scan rapide avec les ports par défaut
python scanner.py -t scanme.nmap.org

# 🔹 Plage des ports réservés
python scanner.py -t scanme.nmap.org -p 1-1024

# 🔹 Liste de ports spécifiques
python scanner.py -t 192.168.1.10 -p 22,80,443,3306,8080

# 🔹 Vitesse maximale avec 200 threads
python scanner.py -t scanme.nmap.org -p 1-5000 -w 200
```

📺 **Exemple de sortie** (à titre illustratif) :

```text
=== PY-NET-RECON v2.3 | Ultimate Threat Intelligence & Forensic Recon Engine ===

[*] Objetivo: scanme.nmap.org | IP: 45.33.32.156 | PTR: scanme.nmap.org
[*] Iniciando motor multihilo con 7 puertos y 100 workers...
[+] Puerto    22 ABIERTO | RTT: 12.34ms | Servicio: SSH (Secure Shell) | CVSS: 5.3 | Riesgo: [MEDIO]

[*] Auditoría integral finalizada en 0.42 segundos.
[+] Reporte Forense Enterprise generado con éxito: reporte_forense_scanme_nmap_org.txt
```

> ℹ️ Les messages affichés par l'outil sont actuellement rédigés en espagnol.
> 🧪 Entraînez-vous dans un cadre légal avec `scanme.nmap.org` (autorisé par le projet Nmap, usage raisonnable) ou dans votre propre laboratoire.
> ⚙️ Plus de threads = plus de rapidité, mais aussi davantage de bruit réseau et un risque de saturation ou de déclenchement d'un IDS/pare-feu.

<a id="fr-arch"></a>

## 🧠 Architecture du code et explications pédagogiques

L'ensemble du code se trouve dans [scanner.py](scanner.py), structuré en **petites fonctions à responsabilité unique**.

```text
 CLI (argparse)
     │   -t cible   -p ports   -w threads
     ▼
 gethostbyname()  ──► IPv4 de la cible ──► gethostbyaddr() ──► PTR
     ▼
 parse_ports()    ──► [21, 22, 80, ...]
     ▼
 ThreadPoolExecutor (N threads)
     ├─► scan_port(ip, 21)  ┐
     ├─► scan_port(ip, 80)  ├─ connect_ex + RTT ─► profil de risque / inspection web
     └─► scan_port(ip, ...) ┘
     ▼
 future.result() ──► liste des ports ouverts
     ▼
 reporte_forense_<cible>.txt ──► inventaire + risque + remédiation
```

| Fonction | Rôle | Détail technique |
|---|---|---|
| `parse_ports()` | 🎛️ Moteur de ports | Texte → `list[int]` ; repli sécurisé sur 80, 443 |
| `get_risk_profile()` | 📊 Cartographie des risques | Service, niveau et profil CVSS estimé du port connu |
| `deep_http_inspection()` | 🛡️ Inspection web | Lecture des en-têtes HTTP sélectionnés et des métadonnées serveur |
| `scan_port()` | 🔌 Unité de travail | Connexion TCP, mesure RTT, risque/bannière et inspection web éventuelle |
| `main()` | 🎼 Orchestrateur | CLI, DNS direct/inverse, pool de threads, sortie et rapport forensique |

### 🧵 Comment circulent les threads ?
1. `main()` crée le pool avec `max_workers = -w`.
2. `executor.submit()` place **une tâche par port** dans la file et renvoie un `Future`.
3. Les threads disponibles prélèvent les tâches ; chacune ouvre **son propre socket** (aucun état partagé → aucune condition de concurrence lors du scan).
4. `future.result()` attend la fin de chaque tâche et récupère sa valeur de retour (`str` ou `None`).
5. À la sortie du bloc `with`, le pool est arrêté proprement.

### 🎓 Ce que vous apprendrez
Les sockets TCP et la poignée de main en trois temps (*three-way handshake*) implicite dans `connect_ex` ; la concurrence pour les tâches liées aux E/S ; la gestion sûre des ressources via les gestionnaires de contexte ; la conception d'une CLI avec `argparse` et la tolérance aux saisies erronées.

### 🔭 Limites connues
Scan TCP/IPv4 de type *connect* uniquement · RTT consigné pour les ports ouverts · CVSS heuristique fondé sur un profil de port, sans validation de vulnérabilité · inspection web en HTTP sans négociation TLS · rapports texte écrasés lors d'un nouveau scan de la même cible · aucun test authentifié, aucune validation d'exploitation ni corrélation CVE.

<a id="fr-disclaimer"></a>

## ⚖️ Avertissement éthique et juridique

> ### 🚨 USAGE STRICTEMENT LÉGAL ET AUTORISÉ 🚨

Cet outil est fourni **exclusivement** pour :
- ✅ le **hacking éthique** et les tests d'intrusion **moyennant autorisation écrite** ;
- ✅ les **audits** de systèmes et de réseaux **dont vous êtes propriétaire** ou pour lesquels vous avez reçu mandat ;
- ✅ la **formation** et la recherche en environnement de laboratoire maîtrisé.

❌ **Toute analyse d'un système sans autorisation expresse est interdite** et peut constituer une infraction pénale. Au Grand-Duché de Luxembourg, l'accès ou le maintien frauduleux dans un système de traitement automatisé de données est notamment réprimé par les articles 509-1 et suivants du Code pénal ; il vous appartient de vérifier la législation applicable dans votre juridiction. L'auteur **décline toute responsabilité** en cas d'usage abusif ou de dommages en résultant. **Vous demeurez seul responsable de vos actes.** 🛡️

<a id="fr-author"></a>

## 👨‍💻 Auteur et vision du projet

**Créé par :** [@francisc0-PE](https://github.com/francisc0-PE)

🌟 py-net-recon a pour ambition de **démontrer qu'un véritable outil de cybersécurité peut être conçu en Python pur**, en maîtrisant chaque composant, du socket jusqu'au rapport. L'objectif : évoluer progressivement vers une boîte à outils de reconnaissance modulaire, pédagogique et professionnelle. 🤝 Les *issues* et *pull requests* sont les bienvenues, et une ⭐ sera appréciée !

<div align="right">

[⬆️ Retour en haut](#top)

</div>

---
---

<a id="zh"></a>

<div align="center">

# 🇨🇳 中文（简体）

[🏠 返回顶部](#top) · [🇬🇧 EN](#en) · [🇪🇸 ES](#es) · [🇫🇷 FR](#fr)

</div>

**📑 目录：** [项目简介](#zh-overview) · [核心功能](#zh-features) · [环境要求](#zh-requirements) · [安装指南](#zh-install) · [使用说明](#zh-usage) · [代码架构](#zh-arch) · [免责声明](#zh-disclaimer) · [作者](#zh-author)

<a id="zh-overview"></a>

## 🎯 项目简介

**py-net-recon** 是一款使用 Python 编写的**网络侦察**工具。它可以找出目标主机上**开放的 TCP 端口**，识别每个端口背后**响应的服务（及其版本）**，并将全部结果保存为带时间戳的报告。

### 🧭 为什么它在渗透测试 / 红队行动的第一阶段至关重要？

所有经授权的渗透都始于**侦察与枚举**。在进行任何评估之前，你必须先弄清：

| ❓ 问题 | 🛠️ py-net-recon 的解决方式 |
|---|---|
| 目标是谁？IP 是多少？ | 正向与反向 DNS（PTR）解析 |
| 哪些"大门"是开着的？ | TCP *connect* 扫描 |
| 每个开放端口的响应速度如何？ | 毫秒级 TCP Socket RTT |
| 可以观察到哪些 Web 防御？ | HTTP 安全响应头检查 |
| 如何确定发现项的优先级？ | 估算 CVSS 分数与风险等级 |
| 如何留存证据？ | 结构化 `.txt` 取证报告 |

> 💡 **攻击面** = 所有暴露在外的入口点。你看不到的东西，就无法防御（也无法审计）。

<a id="zh-features"></a>

## 🚀 核心功能

### 1️⃣ 🔌 基于 Socket 的 TCP 扫描与连接的正确关闭
使用 `socket` 模块，配合 `AF_INET` + `SOCK_STREAM`（TCP/IPv4）以及 `connect_ex()`。该函数**返回错误码而不是抛出异常**：返回 `0` 表示**端口开放**。
- ⏱️ 每个端口 **1.0 秒**超时，被过滤的端口不会阻塞整个扫描。
- 🧹 `with socket.socket(...)` 即使出错也会**始终关闭连接**，避免文件描述符泄漏。

### 2️⃣ ⚡ 使用 `ThreadPoolExecutor` 实现大规模多线程
端口扫描是**I/O 密集型**任务：程序大部分时间都在*等待*网络响应。线程池可以**同时**等待数十个连接。
- 🧵 并发数可配置（`-w`，默认 100）。
- 📈 扫描 1-1024 端口的耗时从数分钟（串行）缩短到数秒。
- 🔒 `with ThreadPoolExecutor` 代码块确保所有线程都会结束并被释放。

### 3️⃣ 🏷️ Banner 抓取（服务特征与版本）
发现端口开放后，程序会新建一次连接并读取服务的首次响应：

| 端口 | 典型服务 | 技术手段 |
|:---:|---|---|
| **22** | SSH | 服务器主动声明：`SSH-2.0-OpenSSH_8.9...` |
| **80 / 8080** | HTTP | 发送 `GET / HTTP/1.1` + `Host` 以检查 Web 服务 |
| **21 / 其他** | FTP 等 | 读取欢迎信息 |

仅保留**第一行**，并以 `errors='ignore'` 解码。无响应时显示 `Sin banner visible`（无可见 Banner）。

### 4️⃣ 🖥️ 基于 `argparse` 的专业命令行界面（CLI）
自动生成帮助（`-h`）、必填参数与类型校验（`-w` 必须为整数）。输出使用 **ANSI 颜色**：🟢 开放、🟡 提示、🔴 错误。

### 5️⃣ 🎛️ 动态端口范围引擎
`parse_ports()` 支持三种格式：

| 格式 | 示例 | 结果 |
|---|---|---|
| 📏 范围 | `1-1024` | 第 1 到第 1024 号端口（含） |
| 📝 列表 | `22,80,443` | 仅这些端口 |
| 🎯 单个 | `8080` | 一个端口 |

输入格式无效时工具不会崩溃：它会给出提示并默认使用 `80, 443`。

### 6️⃣ 🗂️ 自动生成带时间戳的 `.txt` 取证报告
每次运行都会生成 `reporte_forense_<目标>.txt`（点号替换为 `_`），包含目标、解析后的 IP、**精确分析时间**、所选端口、线程数、总耗时和开放端口的详细清单。对同一目标再次扫描会覆盖该文件。

### 7️⃣ 🔁 DNS 反向解析（PTR）
将主机名解析为 IPv4 后，工具调用 `gethostbyaddr()` 查询与该 IP 关联的 PTR 名称。结果会显示在终端并写入报告；没有 PTR 记录时会明确标记。PTR 信息本身不能证明资产归属。

### 8️⃣ ⏱️ 按端口测量 Socket 响应时间（RTT）
工具测量每次 TCP `connect_ex()` 尝试所耗费的时间，并以毫秒表示。**开放端口**的 RTT 会显示并保存在报告中；关闭或无法连接的尝试不会列入发现项清单。这是连接建立耗时，不是持续性网络延迟测试。

### 9️⃣ 🛡️ Web 安全响应头检查
对于选定的 Web 端口（`80`、`443`、`8080`、`8443`、`3000`、`5000`），工具请求根路径并检查 `Strict-Transport-Security`（HSTS）、`X-Frame-Options`、`Content-Security-Policy` 和 `X-Powered-By`，同时记录 `Server` 响应头。响应头缺失或未披露本身并不证明存在漏洞。

> ⚠️ 检查使用普通 HTTP，不会进行 TLS 协商。因此，仅支持 HTTPS 的服务可能返回不完整或不可用的数据；请使用支持 TLS 的 Web 评估工具进行验证。

### 🔟 📊 风险矩阵与估算 CVSS
已知端口会关联服务档案、四种严重程度之一（低、中、高、严重；CLI 标签为 `BAJO`、`MEDIO`、`ALTO` 或 `CRÍTICO`）和**估算的 CVSS 基础分数**。未配置档案的端口标记为 `INFORMATIVO`，分数为 `0.0`。

> ℹ️ 这些是基于端口的启发式估值，并非对已确认漏洞的 CVSS 评估、CVE 匹配或可利用性验证。应结合环境验证发现项后再做风险决策。

### 1️⃣1️⃣ 🧾 企业级取证报告与加固建议
报告包含分析摘要、目标与 PTR 身份、扫描范围和耗时、开放端口/服务清单、RTT 与风险指标、可获取的 Web 响应头观察结果，以及修复与加固章节。建议涵盖不安全协议、Web 防御响应头和敏感服务的网络分段。

<a id="zh-requirements"></a>

## 📦 环境要求与依赖

| 要求 | 说明 |
|---|---|
| 🐍 **Python** | 3.8 或更高版本 |
| 📚 **外部依赖** | **无** ✅ |
| 💻 **操作系统** | Windows、Linux、macOS |

**100% 使用 Python 标准库**：`argparse`、`socket`、`concurrent.futures`、`time`、`datetime`。✨ 无需 `pip install`，便于审计、可移植，非常适合学习扫描器的底层原理。

<a id="zh-install"></a>

## 🛠️ 安装指南

```bash
# 1️⃣ 检查 Python 版本
python --version        # Linux/macOS 请使用：python3 --version

# 2️⃣ 克隆仓库
git clone https://github.com/francisc0-PE/py-net-recon.git
cd py-net-recon

# 3️⃣ 验证是否可用
python scanner.py --help
```

🎉 完成！无需再安装任何东西。

<a id="zh-usage"></a>

## 🎮 使用说明与实战示例

| 参数 | 完整形式 | 必填 | 说明 | 默认值 |
|:---:|---|:---:|---|---|
| `-t` | `--target` | ✅ | 目标 IP 或域名 | — |
| `-p` | `--ports` | ❌ | 范围（`1-1024`）或列表（`80,443`） | `21,22,80,443,445,3306,8080` |
| `-w` | `--workers` | ❌ | 并发线程数 | `100` |
| `-h` | `--help` | ❌ | 显示帮助 | — |

```bash
# 📖 查看帮助
python scanner.py --help

# 🔹 使用默认端口快速扫描
python scanner.py -t scanme.nmap.org

# 🔹 扫描知名端口范围
python scanner.py -t scanme.nmap.org -p 1-1024

# 🔹 扫描指定端口列表
python scanner.py -t 192.168.1.10 -p 22,80,443,3306,8080

# 🔹 使用 200 个线程获得最高速度
python scanner.py -t scanme.nmap.org -p 1-5000 -w 200
```

📺 **输出示例**（仅作演示）：

```text
=== PY-NET-RECON v2.3 | Ultimate Threat Intelligence & Forensic Recon Engine ===

[*] Objetivo: scanme.nmap.org | IP: 45.33.32.156 | PTR: scanme.nmap.org
[*] Iniciando motor multihilo con 7 puertos y 100 workers...
[+] Puerto    22 ABIERTO | RTT: 12.34ms | Servicio: SSH (Secure Shell) | CVSS: 5.3 | Riesgo: [MEDIO]

[*] Auditoría integral finalizada en 0.42 segundos.
[+] Reporte Forense Enterprise generado con éxito: reporte_forense_scanme_nmap_org.txt
```

> ℹ️ CLI 输出及风险标签目前为西班牙语；上方示例展示了 v2.3 的 RTT、CVSS 和 PTR 字段。
> 🧪 请在合法范围内练习：使用 `scanme.nmap.org`（Nmap 项目允许，请适度使用）或你自己的实验环境。
> ⚙️ 线程越多速度越快，但网络噪声也越大，并有可能占满带宽或触发 IDS/防火墙。

<a id="zh-arch"></a>

## 🧠 代码架构与原理讲解

全部代码位于 [scanner.py](scanner.py)，由**职责单一的小函数**组成。

```text
 CLI (argparse)
     │   -t 目标   -p 端口   -w 线程数
     ▼
 gethostbyname()  ──► 目标 IPv4 ──► gethostbyaddr() ──► PTR
     ▼
 parse_ports()    ──► [21, 22, 80, ...]
     ▼
 ThreadPoolExecutor（N 个线程）
     ├─► scan_port(ip, 21)  ┐
     ├─► scan_port(ip, 80)  ├─ connect_ex + RTT ─► 风险档案 / Web 检查
     └─► scan_port(ip, ...) ┘
     ▼
 future.result() ──► 开放端口结果列表
     ▼
 reporte_forense_<目标>.txt ──► 清单 + 风险 + 修复建议
```

| 函数 | 作用 | 技术细节 |
|---|---|---|
| `parse_ports()` | 🎛️ 端口引擎 | 文本 → `list[int]`；安全回退到 80、443 |
| `get_risk_profile()` | 📊 风险映射 | 已知端口的服务、等级与估算 CVSS 档案 |
| `deep_http_inspection()` | 🛡️ Web 检查 | 读取指定 HTTP 响应头和服务器信息 |
| `scan_port()` | 🔌 工作单元 | TCP 连接、RTT 测量、Banner/风险及可选 Web 检查 |
| `main()` | 🎼 调度中枢 | CLI、正向/反向 DNS、线程池、输出与取证报告 |

### 🧵 线程是如何流转的？
1. `main()` 以 `max_workers = -w` 创建线程池。
2. `executor.submit()` 为**每个端口提交一个任务**并返回 `Future`。
3. 空闲线程从队列中领取任务；每个任务打开**各自独立的 socket**（无共享状态 → 扫描本身不存在竞态条件）。
4. `future.result()` 会阻塞直至对应任务结束，并取回返回值（`str` 或 `None`）。
5. 退出 `with` 代码块时，线程池被干净地关闭。

### 🎓 你将学到什么
TCP Socket，以及 `connect_ex` 中隐含的三次握手；I/O 密集型任务的并发；用上下文管理器安全管理资源；用 `argparse` 设计 CLI 并容错处理错误输入。

### 🔭 已知限制
仅支持 TCP/IPv4 *connect* 扫描 · RTT 仅保存在开放端口结果中 · CVSS 是端口档案启发式估值，不验证漏洞 · Web 检查使用 HTTP 且不协商 TLS · 同一目标的纯文本报告会被覆盖 · 不包含认证测试、漏洞利用验证或 CVE 关联。

<a id="zh-disclaimer"></a>

## ⚖️ 道德与法律免责声明

> ### 🚨 仅限合法且经授权的使用 🚨

本工具**仅**可用于：
- ✅ **道德黑客**与渗透测试，且**须获得书面授权**；
- ✅ 对**你自己拥有**或受委托评估的系统与网络进行**审计**；
- ✅ 在受控实验环境中进行**教学**与研究。

❌ **未经明确许可扫描任何系统均被禁止**，并可能依据当地法律构成**计算机犯罪**。对于滥用本工具或由此造成的任何损失，作者**概不负责**。**你须对自己的行为负全部责任。** 🛡️

<a id="zh-author"></a>

## 👨‍💻 作者与项目愿景

**作者：** [@francisc0-PE](https://github.com/francisc0-PE)

🌟 py-net-recon 旨在**证明仅用纯 Python 就能构建真正实用的网络安全工具**，并让开发者理解其中每个环节，从 socket 到最终报告。目标是逐步发展成模块化、可教学、专业的侦察工具包。🤝 欢迎提交 Issue 和 Pull Request，也欢迎点亮 ⭐！

<div align="right">

[⬆️ 返回顶部](#top)

</div>

---

<div align="center">

**🔐 Learn · Build · Audit · Protect 🔐**

*Made with 💚 for the global cybersecurity community.*

</div>
