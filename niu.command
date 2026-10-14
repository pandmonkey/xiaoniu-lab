#!/bin/bash
# Launch via Terminal.app so macOS grants Bluetooth permission to Terminal.
cd "$(dirname "$0")"
PY=./.venv/bin/python
DEV="NIU Link 1691"

echo "NIU BLE tool — target: $DEV (output also logged to session.log)"
while true; do
    echo
    echo "  1) scan      - list nearby BLE devices"
    echo "  2) explore   - dump GATT services/characteristics"
    echo "  3) unlock    - send derestrict frame"
    echo "  4) lock      - restore speed limit"
    echo "  5) quit"
    read -r -p "> " c
    case "$c" in
        1) $PY scan.py 2>&1 | tee -a session.log ;;
        2) $PY explore.py "$DEV" 2>&1 | tee -a session.log ;;
        3) $PY unlock.py "$DEV" 2>&1 | tee -a session.log ;;
        4) $PY unlock.py "$DEV" --lock 2>&1 | tee -a session.log ;;
        5) exit 0 ;;
        *) echo "?" ;;
    esac
done
