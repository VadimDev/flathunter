#!/bin/bash
while true; do
    pipenv run python flathunt.py --config config_kleinanzeigen.yaml &
    PID=$!

    sleep 300

    kill $PID 2>/dev/null

    wait $PID 2>/dev/null

    echo "Restart..."
done
