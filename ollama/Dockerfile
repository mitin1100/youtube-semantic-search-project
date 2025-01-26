FROM python:3.9.11

RUN apt-get update && apt-get install -y curl \
    && curl -fsSL https://install.ollama.com | bash

RUN pip install ollama
RUN ollama download mxbai-embed-large

EXPOSE 8000

CMD ["ollama", "serve"]