#!/usr/bin/env bash
set -xe

source venv/bin/activate
source stock-market/.env

ROOT=$(pwd)
HOST=localhost
PORT=8000

cd "$ROOT/stock-market"
kill -9 "$(lsof -ti:$SM_PORT)" | true
python stock-market.py &
SM_PID=$!

cd "$ROOT/oems"
kill -9 "$(lsof -ti:$PORT)" | true
python manage.py migrate
python manage.py runserver "$HOST:$PORT" &
OEMS_PID=$!

function cleanup() {
    kill -9 "$SM_PID"
    kill -9 "$OEMS_PID"
}
trap cleanup EXIT

wait