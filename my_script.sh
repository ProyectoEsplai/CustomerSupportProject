#!/bin/sh

set -e

VENV_NAME=".venv"
REQS_FILE="requirements.txt"
VENV_PATH="$PWD/$VENV_NAME"
TMP_RC=".venv_shell_rc"
TMP_ZDOTDIR=".venv_zdotdir"
USER_SHELL="${SHELL:-/bin/sh}"
SHELL_NAME="$(basename "$USER_SHELL")"

echo "Creating virtualenv '$VENV_NAME'..."
python3 -m venv "$VENV_NAME"

if [ ! -d "$VENV_NAME" ]; then
    echo "Error: Failed to create the virtual environment."
    exit 1
fi

echo "Installing dependencies in the virtual environment..."
"$VENV_PATH/bin/python" -m pip install --upgrade pip > /dev/null 2>&1

if [ -f "$REQS_FILE" ]; then
    echo "Installing dependencies from $REQS_FILE..."
    "$VENV_PATH/bin/pip" install -r "$REQS_FILE"
else
    echo "Error: $REQS_FILE not found!"
    exit 1
fi

echo "Setup complete! FastAPI environment is ready."

if [ "$SHELL_NAME" = "zsh" ]; then
    mkdir -p "$TMP_ZDOTDIR"
    cat > "$TMP_ZDOTDIR/.zshrc" <<EOF
[ -f ~/.zshrc ] && . ~/.zshrc
. "$VENV_PATH/bin/activate"
echo "Virtual environment '$VENV_NAME' is active."
echo "Type 'deactivate' when you want to leave it."
zshexit() { rm -rf "$PWD/$TMP_ZDOTDIR"; }
EOF
    exec env ZDOTDIR="$PWD/$TMP_ZDOTDIR" "$USER_SHELL" -i
elif [ "$SHELL_NAME" = "bash" ]; then
    cat > "$TMP_RC" <<EOF
[ -f ~/.bashrc ] && . ~/.bashrc
. "$VENV_PATH/bin/activate"
echo "Virtual environment '$VENV_NAME' is active."
echo "Type 'deactivate' when you want to leave it."
rm -f "$PWD/$TMP_RC"
EOF
    exec "$USER_SHELL" --rcfile "$TMP_RC" -i
else
    cat > "$TMP_RC" <<EOF
[ -f ~/.bashrc ] && . ~/.bashrc
. "$VENV_PATH/bin/activate"
echo "Virtual environment '$VENV_NAME' is active."
echo "Type 'deactivate' when you want to leave it."
rm -f "$PWD/$TMP_RC"
EOF
    exec /bin/bash --rcfile "$TMP_RC" -i
fi
