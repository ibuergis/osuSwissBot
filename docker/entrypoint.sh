#!/bin/sh

CONFIG_DIR=/app/config

if [ -z "$(ls -A "$CONFIG_DIR" 2>/dev/null)" ]; then
  echo "Config directory is empty, copying defaults..."
  cp -r /app/config-default/* "$CONFIG_DIR"
fi

exec "$@"
