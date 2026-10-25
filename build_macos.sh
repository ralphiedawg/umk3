echo("Installing dependencies...")

venv/bin/pip install -r requirements.txt

echo("Compiling to app bundle...")
venv/bin/pyinstaller --noconfirm UMK.macOS.spec 
