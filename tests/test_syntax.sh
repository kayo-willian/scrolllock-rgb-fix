#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=== Running Syntax & Static Checks ==="

echo "1. Checking Bash scripts syntax..."
bash -n "$ROOT/install.sh"
bash -n "$ROOT/uninstall.sh"
bash -n "$ROOT/tests/test_syntax.sh"
echo "   -> Bash syntax OK."

echo "2. Compiling Python script..."
python3 -m py_compile "$ROOT/scrolllock-rgb.py"
echo "   -> Python compilation OK."

echo "3. Verifying required files exist..."
for file in scrolllock-rgb.py scrolllock-rgb.service install.sh uninstall.sh README.md LICENSE CONTRIBUTING.md CHANGELOG.md; do
    if [[ ! -f "$ROOT/$file" ]]; then
        echo "ERROR: Missing required file $file" >&2
        exit 1
    fi
done
echo "   -> All required files present."

echo "=== All Static Checks Passed Successfully ==="
