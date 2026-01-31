#!/bin/bash

# Get the absolute path of the directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
USER_HOME="/home/$(whoami)"

echo "Configuring PetriWatch in: $DIR"

# 1. Make the Python script executable
chmod +x "$DIR/petriwatch.py"

# 2. Update and copy the .desktop shortcut
DESKTOP_FILE="$DIR/PetriWatch.desktop"
DESKTOP_DESTINATION="$USER_HOME/Desktop/PetriWatch.desktop"

if [ -f "$DESKTOP_FILE" ]; then
    cp "$DESKTOP_FILE" "$DESKTOP_DESTINATION"
    # Update the Icon and Exec paths dynamically
    sed -i "s|Icon=.*|Icon=$DIR/icon.png|" "$DESKTOP_DESTINATION"
    sed -i "s|Exec=.*|Exec=lxterminal --working-directory=$DIR -e ./petriwatch.py|" "$DESKTOP_DESTINATION"
    chmod +x "$DESKTOP_DESTINATION"
    echo "-> Desktop shortcut created with custom icon."
else
    echo "-> Error: PetriWatch.desktop not found."
fi

# 3. System configuration: Enable Quick Exec
LIBFM_CONF="$USER_HOME/.config/libfm/libfm.conf"
if [ -f "$LIBFM_CONF" ]; then
    sed -i 's/quick_exec=0/quick_exec=1/' "$LIBFM_CONF"
    echo "-> System Quick Exec enabled in libfm.conf."
else
    mkdir -p "$(dirname "$LIBFM_CONF")"
    echo -e "[config]\nquick_exec=1" > "$LIBFM_CONF"
    echo "-> System Quick Exec configured."
fi

# 4. Refresh Desktop Manager
pcmanfm --reconfigure > /dev/null 2>&1
pcmanfm --desktop --reconfigure > /dev/null 2>&1

echo "PetriWatch Installation Complete!"
echo "NOTE: If the shortcut still asks for confirmation,"
echo "please REBOOT your Raspberry Pi to apply changes."
