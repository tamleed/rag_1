# RAG Service

## 🚀 Запуск локально
```bash
uvicorn app.main:app --reload --port 8000
```

## 🐳 Docker
```bash
docker-compose up -d --build
```

## ⚙️ Systemd
```bash
sudo cp docs/rag.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable rag
sudo systemctl start rag
```

## 📡 API
- `GET /api/health`
- `POST /api/query`
