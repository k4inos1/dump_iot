import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import time
import os
import json
import base64
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# --- CONFIGURACIÓN ---
# Opción A: Nombre del archivo (si existe)
CREDENTIALS_FILE = 'kainos-auditor-firebase-adminsdk-fbsvc-73a8a245ad.json'

# Opción B: Variable de entorno (Base64 del JSON)
ENV_CREDENTIALS = os.getenv('FIREBASE_CREDENTIALS_BASE64')

# URL de tu base de datos
DATABASE_URL = 'https://kainos-auditor-default-rtdb.firebaseio.com/'

def init_firebase():
    """Inicializa la conexión con Firebase (Soporta .env y archivo .json)"""
    
    # Evitar reinicializar si ya existe
    if firebase_admin._apps:
        return True

    cred = None

    # 1. Intentar cargar desde Variable de Entorno (.env)
    if ENV_CREDENTIALS:
        try:
            print("🔑 Intentando cargar credenciales desde .env...")
            decoded_bytes = base64.b64decode(ENV_CREDENTIALS)
            cred_dict = json.loads(decoded_bytes)
            cred = credentials.Certificate(cred_dict)
            print("✅ Credenciales cargadas desde .env")
        except Exception as e:
            print(f"⚠️ Error leyendo .env: {e}")

    # 2. Si falló lo anterior, intentar cargar desde archivo .json
    if not cred:
        if os.path.exists(CREDENTIALS_FILE):
            print(f"📂 Cargando credenciales desde archivo: {CREDENTIALS_FILE}")
            cred = credentials.Certificate(CREDENTIALS_FILE)
        else:
            print("❌ ERROR CRÍTICO: No se encontraron credenciales (ni en .env ni archivo .json)")
            return False

    # 3. Conectar
    try:
        firebase_admin.initialize_app(cred, {
            'databaseURL': DATABASE_URL
        })
        print("🔥 Firebase Conectado Exitosamente")
        return True
    except Exception as e:
        print(f"❌ Error conectando a Firebase: {e}")
        return False

def push_test_data():
    """Sube datos de prueba para verificar que funciona"""
    try:
        # Creamos una referencia en la base de datos (como una carpeta)
        ref = db.reference('auditoria/estado_sistema')
        
        # Datos a subir
        data = {
            'estado': 'ONLINE',
            'dispositivo': 'Raspberry Pi 3B+ (Kainos)',
            'timestamp': time.time(),
            'mensaje': 'Conexión exitosa desde el script Python 🐍'
        }
        
        # Subir los datos
        ref.set(data)
        print("✅ ¡Datos enviados a la nube! Revisa tu consola de Firebase.")
        
    except Exception as e:
        print(f"❌ Error subiendo datos: {e}")

if __name__ == "__main__":
    print("--- INICIANDO SISTEMA KAINOS AUDITOR ---")
    if init_firebase():
        push_test_data()
