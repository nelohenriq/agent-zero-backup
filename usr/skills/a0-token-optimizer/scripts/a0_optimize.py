#!/usr/bin/env python3
import json
import os
import sys

SETTINGS_PATH = '/a0/usr/settings.json'
PROMPT_BEHAVIOUR_PATH = '/a0/prompts/agent.system.behaviour.md'

def load_settings():
    if not os.path.exists(SETTINGS_PATH):
        return {}
    with open(SETTINGS_PATH, 'r') as f:
        return json.load(f)

def save_settings(settings):
    with open(SETTINGS_PATH, 'w') as f:
        json.dump(settings, f, indent=4)

def apply_preset(mode='standard'):
    settings = load_settings()
    
    if mode == 'standard':
        settings['chat_model_ctx_length'] = 50000
        settings['chat_model_ctx_history'] = 0.5
        settings['chat_model_kwargs'] = settings.get('chat_model_kwargs', {})
        settings['chat_model_kwargs']['max_tokens'] = 2048
        settings['chat_model_kwargs']['temperature'] = 0.2
        settings['workdir_max_lines'] = 100
        settings['memory_recall_history_len'] = 5000
    elif mode == 'aggressive':
        settings['chat_model_ctx_length'] = 30000
        settings['chat_model_ctx_history'] = 0.4
        settings['chat_model_kwargs'] = settings.get('chat_model_kwargs', {})
        settings['chat_model_kwargs']['max_tokens'] = 1024
        settings['chat_model_kwargs']['temperature'] = 0.1
        settings['workdir_max_lines'] = 50
        settings['memory_recall_history_len'] = 2000
    
    save_settings(settings)
    print(f"Applied {mode} optimization preset to {SETTINGS_PATH}")

def main():
    if len(sys.argv) < 2:
        print("Usage: a0_optimize.py [apply|status]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    if cmd == 'apply':
        mode = sys.argv[2] if len(sys.argv) > 2 else 'standard'
        apply_preset(mode)
    elif cmd == 'status':
        settings = load_settings()
        print(json.dumps({
            "ctx_length": settings.get('chat_model_ctx_length'),
            "ctx_history": settings.get('chat_model_ctx_history'),
            "max_tokens": settings.get('chat_model_kwargs', {}).get('max_tokens'),
            "temperature": settings.get('chat_model_kwargs', {}).get('temperature')
        }, indent=2))

if __name__ == "__main__":
    main()
