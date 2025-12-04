import base64
import os

# Nombre de tu archivo JSON original
JSON_FILE = 'kainos-auditor-firebase-adminsdk-fbsvc-73a8a245ad.json'
ENV_FILE = '.env'

def convert_to_env():
    if not os.path.exists(JSON_FILE):
        print(f"❌ No encuentro el archivo {JSON_FILE}")
        return

    # Leer el JSON y convertirlo a Base64
    with open(JSON_FILE, 'rb') as f:
        json_content = f.read()
        encoded_content = base64.b64encode(json_content).decode('utf-8')

    # Crear el contenido del .env
    env_content = f"FIREBASE_CREDENTIALS_BASE64={encoded_content}\n"

    # Escribir el archivo .env
    with open(ENV_FILE, 'w') as f:
        f.write(env_content)

    print(f"✅ ¡Listo! Se ha creado el archivo '{ENV_FILE}' con tus credenciales encriptadas.")
    print("🔒 Ahora puedes borrar el archivo .json original si quieres (pero guárdalo en un lugar seguro por si acaso).")
    print("📝 Recuerda agregar .env a tu .gitignore")

if __name__ == "__main__":
    convert_to_env()
