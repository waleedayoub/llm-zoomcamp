docker run -d -p 3000:8080 \
    --gpus all \
    -e OLLAMA_BASE_URL=http://192.168.50.49:11434 \
    -v open-webui:/app/backend/data \
    --name open-webui \
    --restart always \
    ghcr.io/open-webui/open-webui:main