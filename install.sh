#!/bin/bash

# Detect the absolute path where the folder is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
USER_DESKTOP="/home/$(whoami)/Desktop"

echo "Configuring PetriWatch in: $DIR"

# 1. Set execution permissions for the script and the icon
chmod +x "$DIR/petriwatch.py"
chmod 644 "$DIR/icon.png"

# 2. Create the Desktop shortcut
DESKTOP_FILE="$DIR/PetriWatch.desktop"
FINAL_DESKTOP="$USER_DESKTOP/PetriWatch.desktop"

if [ -f "$DESKTOP_FILE" ]; then
    tr -d '\r' < "$DESKTOP_FILE" > "$FINAL_DESKTOP"
    
    # Replace the PLACEHOLDER with the actual path
    sed -i "s|PATH_HERE|$DIR|g" "$FINAL_DESKTOP"
    
    # Ensure the shortcut is executable
    chmod +x "$FINAL_DESKTOP"
    echo "-> Desktop shortcut created."
else
    echo "-> ERROR: PetriWatch.desktop not found in the current folder!"
    exit 1
fi

# 3. Enable Quick Exec in system config
LIBFM_CONF="/home/$(whoami)/.config/libfm/libfm.conf"
if [ -f "$LIBFM_CONF" ]; then
    sed -i 's/quick_exec=0/quick_exec=1/' "$LIBFM_CONF"
else
    mkdir -p "$(dirname "$LIBFM_CONF")"
    echo -e "[config]\nquick_exec=1" > "$LIBFM_CONF"
fi

# 4. Refresh the system desktop manager to apply changes
pcmanfm --reconfigure > /dev/null 2>&1
pcmanfm --desktop --reconfigure > /dev/null 2>&1
touch "$FINAL_DESKTOP"

echo "Installation Complete!"
echo "If the icon is still not visible, please reboot your Raspberry Pi."
