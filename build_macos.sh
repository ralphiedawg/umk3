echo("Installing dependencies...")

venv/bin/pip install -r requirements.txt

echo("Compiling to app bundle...")
venv/bin/pyinstaller \
  --name "UMK" \
  --windowed \
  --onedir \
  --noconfirm \
  --clean \
  --osx-bundle-identifier "com.umk.app" \
  --add-data "config:config" \
  --add-data "icons:icons" \
  --add-data "hand_landmarker.task:." \
  --icon "macos_apps/oldumk.app/Contents/Resources/AppIcon.icns" \
  --paths "." \
  src/tray/GenericTray.py
