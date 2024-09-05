#!/bin/bash
while true; do
    pipenv run python flathunt.py --config config_kleinanzeigen.yaml &
    PID=$!

    sleep 600

    kill $PID 2>/dev/null

    wait $PID 2>/dev/null

    echo "Программа завершена. Перезапуск..."
done
