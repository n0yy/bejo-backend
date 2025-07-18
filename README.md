# Panduan Deployment Docker

## Persiapan

1. **Pastikan Docker terinstall**

   ```bash
   docker --version
   docker-compose --version
   ```

2. **Buat file .env**
   ```env
   QDRANT_HOST=localhost
   QDRANT_PORT=6333
   OLLAMA_URL=http://localhost:11434
   OLLAMA_EMBEDDING_MODEL=nomic-embed-text
   OLLAMA_LLM_MODEL=qwen2.5:7b
   ```

## Cleanup (Opsional)

```bash
# Hapus semua containers dan images
docker system prune -af --volumes
```

## Build dan Start

### Mode CPU

```bash
# Build dan start
docker-compose --profile cpu up -d --build

# Atau jika sudah di-build sebelumnya
docker-compose --profile cpu up -d
```

### Mode GPU

```bash
# Build dan start
docker-compose --profile gpu up -d --build

# Atau jika sudah di-build sebelumnya
docker-compose --profile gpu up -d
```

## Monitoring

```bash
# Lihat logs
docker-compose logs -f bejo-backend

# Cek status container
docker-compose ps

# Health check
curl http://localhost:8000/health
```

## Management

```bash
# Stop services
docker-compose down

# Restart
docker-compose restart

# Rebuild image
docker-compose build --no-cache
```

## Troubleshooting

```bash
# Masuk ke container
docker exec -it <container_name> bash

# Cek logs detail
docker logs <container_name>
```
