#!/usr/bin/env bash
set -o errexit
pip install -r requirements.txt
npm install -g pnpm
cd frontend
pnpm install
pnpm run build
cd ..