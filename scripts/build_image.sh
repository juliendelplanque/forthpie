#/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

PYTHON="pypy3"

SCRIPT_PATH=`realpath $0`
SCRIPT_DIR=`dirname $SCRIPT_PATH`
FORTHSRC_DIR="$SCRIPT_DIR/../forthsrc"

SNAPSHOT_SCRIPT="$SCRIPT_DIR/snapshot.f"
BYE_SCRIPT="$SCRIPT_DIR/bye.f"
GENERATED_IMAGE_NAME="memory.image"

cat $@ "$SNAPSHOT_SCRIPT" "$BYE_SCRIPT" | $PYTHON -m forthpie.eforth.eforth16bits bootstrap-run

mv "$GENERATED_IMAGE_NAME" "core.image"