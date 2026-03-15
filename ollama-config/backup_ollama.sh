#!/bin/bash
# Ollama Configuration Backup Script
# Run this on the host machine where ollama container is running
# This backs up ollama config WITHOUT models (to save space)

BACKUP_DIR="./ollama-config"
mkdir -p "$BACKUP_DIR"

echo "Backing up Ollama configuration..."

# Find ollama config directory
OLLAMA_PATH=$(docker exec ollama sh -c 'ls -d /root/.ollama /usr/share/ollama 2>/dev/null | head -1')

if [ -z "$OLLAMA_PATH" ]; then
 echo "ERROR: Could not find ollama config directory"
 exit 1
fi

echo "Found ollama config at: $OLLAMA_PATH"

# Create config backup (excluding models)
docker exec ollama tar -czvf /tmp/ollama_config.tar.gz \
 --exclude='models' \
 --exclude='*.gguf' \
 --exclude='*.bin' \
 -C "$(dirname $OLLAMA_PATH)" "$(basename $OLLAMA_PATH)" 2>/dev/null

# Copy backup from container
docker cp ollama:/tmp/ollama_config.tar.gz "$BACKUP_DIR/"

# Export model list (for re-pulling)
docker exec ollama ollama list > "$BACKUP_DIR/models_list.txt" 2>/dev/null

# Export modelfile for each model (preserves customizations)
mkdir -p "$BACKUP_DIR/modelfiles"
while read -r name rest; do
 [ -n "$name" ] && [ "$name" != "NAME" ] && docker exec ollama ollama show "$name" --modelfile > "$BACKUP_DIR/modelfiles/${name}.modelfile" 2>/dev/null
done < "$BACKUP_DIR/models_list.txt"

echo "Backup complete!"
echo "Config: $BACKUP_DIR/ollama_config.tar.gz"
echo "Models list: $BACKUP_DIR/models_list.txt"
echo "Modelfiles: $BACKUP_DIR/modelfiles/"
echo ""
echo "To restore, run: ./restore_ollama.sh"
