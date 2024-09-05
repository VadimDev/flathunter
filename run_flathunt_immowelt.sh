#!/bin/bash
while true; do
    pipenv run python flathunt.py &
    PID=$!

    sleep 600

    kill $PID 2>/dev/null

    wait $PID 2>/dev/null

    echo "Программа завершена. Перезапуск..."
done