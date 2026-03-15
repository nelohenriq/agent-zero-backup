# Agent Zero Configuration Backup

This repository contains Agent Zero configurations and content, ready to restore or deploy.

## Repository Structure

```
├── usr/                    # Agent Zero user data
│   ├── agents/            # Custom agent configurations
│   ├── chats/             # Chat history (metadata only, messages excluded)
│   ├── custom_agents/     # Custom agent definitions
│   ├── knowledge/         # Knowledge base files
│   ├── memory/            # Agent memory storage
│   ├── profiles/          # User profiles
│   ├── projects/          # Project workspaces
│   ├── scheduler/         # Scheduled task configurations
│   ├── shared_knowledge/  # Shared knowledge resources
│   └── skills/            # Custom skills
├── conf/                   # Agent Zero configuration files
│   └── model_providers.yaml
├── docker/                 # Docker configuration files
│   ├── base/              # Base image build files
│   └── run/               # Runtime image build files
├── ollama-config/          # Ollama configuration backup (see below)
└── README.md
```

## Restoring Agent Zero

1. Clone this repository
2. Copy contents to your Agent Zero installation:
   ```bash
   cp -r usr/* /a0/usr/
   cp -r conf/* /a0/conf/
   ```

## Ollama Setup

Ollama runs in a separate container. To backup and restore Ollama configuration **without models**:

### Backup Ollama Config (run on host with ollama container)

```bash
# Create ollama config backup (excluding models)
docker exec ollama tar -czvf /tmp/ollama_config.tar.gz \
  --exclude='models' \
  -C /root/.ollama . 2>/dev/null || \
docker exec ollama tar -czvf /tmp/ollama_config.tar.gz \
  --exclude='models' \
  -C /usr/share/ollama . 2>/dev/null

# Copy backup from container
docker cp ollama:/tmp/ollama_config.tar.gz ./ollama-config/

# List installed models (for reference)
docker exec ollama ollama list > ./ollama-config/models_list.txt
```

### Restore Ollama Config

```bash
# Copy config to container
docker cp ./ollama-config/ollama_config.tar.gz ollama:/tmp/

# Extract config
docker exec ollama tar -xzvf /tmp/ollama_config.tar.gz -C /root/.ollama/

# Re-pull models manually (they are not backed up)
while read model; do
  docker exec ollama ollama pull "$model"
done < ./ollama-config/models_list.txt
```

### Running with Docker Compose

Create a combined `docker-compose.yml`:

```yaml
services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    restart: unless-stopped

  agent-zero:
    image: agent0ai/agent-zero:latest
    container_name: agent-zero
    ports:
      - "50080:80"
    volumes:
      - ./agent-zero:/a0
    depends_on:
      - ollama
    environment:
      - OLLAMA_HOST=http://ollama:11434
    restart: unless-stopped

volumes:
  ollama_data:
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Required API keys (at least one)
OLLAMA_API_KEY=your_key
OPENROUTER_API_KEY=your_key
# ... other providers
```

## Notes

- **Models are NOT included** to save storage space
- **Chat messages are excluded** for privacy
- **Secrets/env files** must be configured manually
- Large data files (node_modules, caches) are excluded via .gitignore

---

**Backup created:** $(date)
