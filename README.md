# CEU-HortensIA

> ### Proyecto desarrollado en colaboración con **HP Inc.**

> Asistente domótico-asistencial para personas con Alzheimer o discapacidad visual.
> Detecta objetos y escenas en tiempo real mediante la cámara del móvil, evalúa riesgos en entornos domésticos (probado especialmente en cocina) y avisa por audio (TTS) cuando detecta una situación de peligro.

**Stack:** React Native 0.83 (iOS) · Python 3.12 + FastAPI · PostgreSQL 15 · Ultralytics YOLO (modelo YOLO26s)

---

## Demo rápida (Docker) 

Esta demo levanta **únicamente el servidor de detección** y permite probarlo enviando imágenes guardadas, simulando lo que haría la app móvil.

> **Requisito único:** tener [Docker](https://docs.docker.com/get-docker/) instalado con Docker Compose v2 (comando `docker compose`). El procesamiento es **solo CPU**, por lo que es totalmente portable.

Todos los comandos se ejecutan desde la carpeta `src/` del repositorio.

**1. Levanta el servidor de detección**

```bash
cd src
docker compose up --build server
```

La primera vez se construye la imagen (descarga de dependencias y de torch CPU). Cuando aparezca el log de `uvicorn` escuchando en `0.0.0.0:8888`, el servidor está listo. La documentación interactiva de la API queda disponible en <http://localhost:8888/docs>.

**2. Ejecuta el simulador (en otra terminal, desde `src/`)**

```bash
docker compose run --rm simulator
```

El simulador lee cada imagen de `src/backend/demo/samples/`, la envía al servidor por WebSocket (igual que la app móvil) e imprime una tabla con los objetos detectados (clase, confianza, zona, riesgo doméstico —`dom_risk`: LOW/MEDIUM/HIGH—, riesgo contextual —`obj_risk`: 0–1— y si se aproxima) y la evaluación de riesgo de la escena (instantáneo, suavizado y severidad INFO/WARNING/CRITICAL).

```bash
# Enviar cada imagen 5 veces con 0,3 s entre frames (ejercita el seguimiento temporal)
docker compose run --rm simulator \
  python -m backend.demo.simulate_client --repeat 5 --delay 0.3
```

**3. Apaga todo**

```bash
docker compose down
```

> En esta demo el servidor corre en **modo demo** (`HORTENSIA_DEMO_MODE=1`): se omite la validación de sesión contra la base de datos para poder probar el detector de forma aislada. La app iOS, la autenticación, los usuarios y PostgreSQL quedan fuera de este flujo. Para levantar la **aplicación completa**, sigue la [instalación paso a paso](#instalación-paso-a-paso).

---

## Índice

1. [Demo rápida (Docker)](#-demo-rápida-docker--recomendado-para-evaluación)
2. [Finalidad](#finalidad)
3. [Arquitectura](#arquitectura)
4. [Requisitos previos](#requisitos-previos)
5. [Instalación paso a paso](#instalación-paso-a-paso)
   - [1. Clonar el repositorio](#1-clonar-el-repositorio)
   - [2. Base de datos (PostgreSQL)](#2-base-de-datos-postgresql)
   - [3. Backend (Python / FastAPI)](#3-backend-python--fastapi)
   - [4. Frontend (React Native)](#4-frontend-react-native)
   - [5. Configurar Xcode y el iPhone (primera vez)](#5-configurar-xcode-y-el-iphone-primera-vez)
6. [Arranque y parada](#arranque-y-parada)
7. [Limitaciones y entorno probado](#limitaciones-y-entorno-probado)

---

## Finalidad

**CEU-HortensIA** es un asistente pensado para apoyar de forma autónoma a personas mayores con Alzheimer u otras condiciones cognitivas, así como a personas con discapacidad visual, en su entorno doméstico cotidiano.

La aplicación utiliza la cámara trasera del iPhone para capturar el entorno y enviarlo al backend, donde un modelo de visión por computador (**YOLO26s**) identifica objetos y evalúa el nivel de riesgo de la escena. Si se detecta peligro (p. ej. objetos cortantes accesibles), la aplicación notifica al usuario mediante síntesis de voz (TTS) directamente en el teléfono, sin necesidad de interacción manual.

---

## Arquitectura

```
src/
├── config.json            ← Configuración central (puertos, usuario BBDD, dispositivo iOS)
├── yolo26s.pt             ← Pesos del modelo YOLO26s
├── Dockerfile             ← Imagen de la demo (servidor de detección, solo CPU)
├── docker-compose.yml     ← Orquestación de la demo (server + simulador)
├── backend/               ← API REST (FastAPI) + IA (YOLO) + repositorios (SQLAlchemy)
│   └── demo/              ← Simulador WebSocket e imágenes de prueba (demo Docker)
├── frontend/              ← App iOS (React Native 0.83)
└── scripts/               ← Scripts de arranque y parada
```

El backend expone una API REST en `http://localhost:8888` y una conexión WebSocket para el streaming de la cámara. La documentación interactiva de la API está disponible en `http://<host>:8888/docs` cuando el servidor está corriendo.

---

## Requisitos previos

> Para la **demo rápida** solo necesitas [Docker](https://docs.docker.com/get-docker/) con Docker Compose v2. Los requisitos siguientes son para instalar la **aplicación completa** (app iOS incluida).

> Plataforma requerida: **macOS** con **Xcode** instalado. El frontend iOS no puede compilarse en Windows ni en Linux.

| Herramienta | Versión mínima | Instalación |
|---|---|---|
| Xcode + Command Line Tools | última estable | App Store + `xcode-select --install` |
| Homebrew | — | [brew.sh](https://brew.sh) |
| Node.js | ≥ 20 | `brew install node` |
| Python | 3.12+ | `brew install python3` |
| PostgreSQL | 15 | `brew install postgresql@15` |
| CocoaPods | — | `brew install cocoapods` |
| Watchman | — | `brew install watchman` (recomendado para Metro) |

---

## Instalación paso a paso

### 1. Clonar el repositorio

```bash
git clone https://gitlab.com/HP-SCDS/Observatorio/2025-2026/hortensia/ceu-hortensia.git
cd HortensIA
```

### 2. Base de datos (PostgreSQL)

**2.1. Arrancar el servicio**

```bash
brew services start postgresql@15
```

**2.2. Añadir PostgreSQL al PATH**

```bash
echo 'export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**2.3. Crear usuario y base de datos**

```bash
# Sustituye <tu_usuario> por el usuario de tu sesión macOS
createuser -s <tu_usuario>
createdb HortensIA
```

**2.4. Editar `src/config.json`**

Abre el fichero `src/config.json` y cambia el campo `database.postgresql.user` por tu usuario de macOS

```json
"database": {
  "postgresql": {
    "host": "localhost",
    "port": 5432,
    "database": "HortensIA",
    "user": "<tu_usuario>"
  }
}
```

> **Nota:** La conexión usa autenticación local (sin contraseña). Si tu PostgreSQL pide contraseña, añádela en la variable `db_password` dentro de `src/backend/databases/connection.py`.

**2.5. Inicializar las tablas**

```bash
cd src
source backend/.tfg/bin/activate   # activa el venv (créalo antes si no existe, ver paso 3)
python -m backend.databases.create_tables
```

---

### 3. Backend (Python / FastAPI)

```bash
cd src/backend

# Crear el entorno virtual
python3 -m venv .tfg
source .tfg/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

El modelo YOLO26s ya está incluido en el repositorio como `src/yolo26s.pt`; no es necesario descargarlo por separado.

---

### 4. Frontend (React Native)

```bash
cd src/frontend

# Instalar dependencias Node
npm install
```

**Instalar pods de iOS**


```bash
# Descargar el tarball de Hermes desde Maven Central
curl -L -o /tmp/hermes-ios-debug.tar.gz \
  "https://repo1.maven.org/maven2/com/facebook/hermes/hermes-ios/0.14.1/hermes-ios-0.14.1-hermes-ios-debug.tar.gz"

# Instalar los pods usando el tarball local
cd ios && HERMES_ENGINE_TARBALL_PATH=/tmp/hermes-ios-debug.tar.gz pod install && cd ..
```

---

### 5. Configurar Xcode y el iPhone (primera vez)

Estos pasos sólo son necesarios la primera vez que se instala la app en un iPhone físico.

**5.1. Abrir el workspace en Xcode**

```
src/frontend/ios/TFG.xcworkspace
```

Abre **siempre** el fichero `.xcworkspace`, no el `.xcodeproj`.

**5.2. Firma del código (Signing)**

1. Xcode → **Settings → Accounts** → añade tu Apple ID si no está.
2. Selecciona el target `TFG` en el panel de la izquierda.
3. Pestaña **Signing & Capabilities** → activa **Automatically manage signing**.
4. Elige tu cuenta en **Team** (un Personal Team de Apple ID gratuito es suficiente para desarrollo local).
5. Si el *Bundle Identifier* actual ya está registrado, cámbialo por algo único (p. ej. `com.tunombre.tfg`).

**5.3. Conectar el iPhone por USB (primera vez)**

1. Conecta el iPhone al Mac mediante **cable USB** (Lightning o USB-C según el modelo).
2. Desbloquea el iPhone y, si aparece el diálogo, pulsa **"Confiar en este ordenador"** y confirma con tu código.

**5.4. Activar el Modo Desarrollador en el iPhone**

En el iPhone: **Ajustes → Privacidad y seguridad → Modo Desarrollador** → actívalo y reinicia el dispositivo cuando se pida.

**5.5. Confiar en el perfil del desarrollador**

Tras instalar la app la primera vez, iOS la bloqueará hasta que confíes en el certificado:

**Ajustes → General → VPN y gestión de dispositivos** → tu Apple ID → **Confiar**

**5.6. Configurar el nombre del dispositivo**

Edita `src/config.json` y cambia `frontend.ios.device` por el nombre exacto de tu iPhone tal como aparece en **Ajustes → General → Información → Nombre** (por defecto hay un nombre personal que no coincidirá con el tuyo):

```json
"frontend": {
  "ios": {
    "device": "<Nombre de tu iPhone>"
  }
}
```

**5.7. Permisos en el primer arranque**

La app solicitará permisos de **Cámara** y **Notificaciones**. Es necesario aceptarlos todos para que funcione correctamente.

---

## Arranque y parada

Todos los scripts se ejecutan desde la **raíz del repositorio** (`ceu-hortensia/`).

### Simulador iOS

```bash
# Arrancar PostgreSQL + backend + simulador
sh src/scripts/start.sh

# Parar todo
sh src/scripts/stop.sh
```

### iPhone físico (recomendado)

Mac e iPhone deben estar conectados a la **misma red Wi-Fi**. El script detecta automáticamente la IP local del Mac y la inyecta en `src/frontend/config.ts`.

```bash
# Arrancar PostgreSQL + backend (0.0.0.0:8888) + compilar y lanzar en el iPhone
sh src/scripts/start_device.sh

# Parar todo (la app en el iPhone se cierra manualmente)
sh src/scripts/stop_device.sh
```

### URLs útiles

| Recurso | URL |
|---|---|
| API REST (docs) | `http://<IP_Mac>:8888/docs` |
| Logs del backend | `tail -f /tmp/backend.log` |

---

## Limitaciones y entorno probado

- **Dispositivo probado:** iPhone 14 Pro. Debería funcionar en cualquier iPhone moderno compatible con React Native 0.83 (iOS 16+), aunque no se ha verificado en otros modelos.
- **Entorno de desarrollo:** MacBook Pro con chip Apple Silicon (M1). Xcode es **obligatorio** para compilar la app iOS; el frontend no puede construirse en Windows ni en Linux.
- **Escenario validado:** entorno doméstico, con especial énfasis en **cocina**. El rendimiento de detección puede variar en otros contextos.
- **Red local (LAN):** el backend no implementa TLS ni autenticación de red. No está preparado para exposición en Internet.
- **Base de datos:** PostgreSQL local sin contraseña (autenticación trust local). Debe securizarse antes de cualquier despliegue real.

---

*Proyecto desarrollado como Trabajo de Fin de Grado (TFG) — CEU Universidad San Pablo.*
