#!/usr/bin/env bash
set -e
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

npm --prefix "$ROOT_DIR/frontend" install
npm --prefix "$ROOT_DIR/frontend" run start
