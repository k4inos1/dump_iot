import os
import sys
import subprocess

def check_dependencies():
    """Verifica e instala dependencias automáticamente en Windows."""
    required = ["customtkinter", "firebase-admin", "pillow", "rich"]
    
    print("🔍 Verificando dependencias...")
    try:
        import customtkinter
        import firebase_admin
        import PIL
        import rich
        print("✅ Todo listo.")
    except ImportError:
        print("⚠️ Faltan librerías. Instalando...")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + required)
        print("✅ Instalación completada.")

if __name__ == "__main__":
    check_dependencies()
    print("\n🚀 INICIANDO KAINOS CONSOLE...")
    
    # Lanzar la GUI principal
    try:
        import console
        app = console.KainosGUI()
        app.mainloop()
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        input("Presione Enter para salir...")