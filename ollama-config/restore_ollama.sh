#!/bin/bash
# Ollama Configuration Restore Script

BACKUP_DIR="./ollama-config"

echo "Restoring Ollama configuration..."

# Copy config to container
docker cp "$BACKUP_DIR/ollama_config.tar.gz" ollama:/tmp/

# Find ollama config directory
OLLAMA_PATH=$(docker exec ollama sh -c 'ls -d /root/.ollama /usr/share/ollama 2>/dev/null | head -1')

if [ -z "$OLLAMA_PATH" ]; then
 echo "ERROR: Could not find ollama config directory"
 exit 1
fi

# Extract config
docker exec ollama tar -xzvf /tmp/ollama_config.tar.gz -C /

echo "Configuration restored!"
echo ""
echo "Now re-pulling models (this may take a while)..."

# Re-pull models
while read -r name rest; do
 if [ -n "$name" ] && [ "$name" != "NAME" ]; then
 echo "Pulling $name..."
 docker exec ollama ollama pull "$name"
 fidone < "$BACKUP_DIR/models_list.txt"

echo "Restore complete!"
