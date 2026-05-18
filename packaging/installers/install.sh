#!/usr/bin/env sh
set -eu

PREFIX="${PREFIX:-$HOME/.local}"
BIN_DIR="$PREFIX/bin"
APP_DIR="$PREFIX/share/panclaw"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
ROOT_DIR="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"

mkdir -p "$BIN_DIR" "$APP_DIR"
cp -R "$ROOT_DIR/src/panclaw" "$APP_DIR/panclaw"

cat > "$BIN_DIR/panclaw" <<'EOF'
#!/usr/bin/env sh
PYTHONPATH="${PANCLAW_HOME:-$HOME/.local/share/panclaw}" exec python3 -m panclaw "$@"
EOF

chmod +x "$BIN_DIR/panclaw"
echo "PanClaw installed to $APP_DIR"
echo "Add $BIN_DIR to PATH if needed."

