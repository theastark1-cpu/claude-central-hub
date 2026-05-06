#!/bin/bash
export PATH="$HOME/.local/node/bin:$PATH"
exec npm run dev -- --port 5173 --host
