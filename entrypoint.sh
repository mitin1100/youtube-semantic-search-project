#!/bin/sh
set -e

# Start Ollama in the background
ollama serve &

# Wait for the Ollama service to be ready
sleep 5

# Pull the specific model
ollama pull mxbai-embed-large

# Keep the container running
tail -f /dev/null