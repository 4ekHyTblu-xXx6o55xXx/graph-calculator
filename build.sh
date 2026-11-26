#!/bin/sh
set -e
# проверяем синтаксис модулей и запуск cli
python3 -m compileall -q src tests
python3 -m src.cli --help > /dev/null
