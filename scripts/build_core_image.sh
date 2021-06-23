#/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

SCRIPT_PATH=`realpath $0`
SCRIPT_DIR=`dirname $SCRIPT_PATH`
FORTHSRC_DIR="$SCRIPT_DIR/../forthsrc"

$SCRIPT_DIR/build_image.sh "$FORTHSRC_DIR/core.f" "$FORTHSRC_DIR/tools.f"