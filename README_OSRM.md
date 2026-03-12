# OSRM Local

Objetivo: usar rota real sem custo por requisicao em producao.

## 1. Preparar o mapa

Use o `docker-compose.yml` ja versionado e gere os artefatos do OSRM uma vez.

Exemplo com o extrato Sul do Brasil:

```powershell
mkdir data\osrm
Invoke-WebRequest -Uri "https://download.geofabrik.de/south-america/brazil/sul-latest.osm.pbf" -OutFile "data/osrm/sul-latest.osm.pbf"
docker run -t -v "${PWD}/data/osrm:/data" ghcr.io/project-osrm/osrm-backend:latest osrm-extract -p /opt/car.lua /data/sul-latest.osm.pbf
docker run -t -v "${PWD}/data/osrm:/data" ghcr.io/project-osrm/osrm-backend:latest osrm-partition /data/sul-latest.osrm
docker run -t -v "${PWD}/data/osrm:/data" ghcr.io/project-osrm/osrm-backend:latest osrm-customize /data/sul-latest.osrm
```

Se preferir o mapa completo do Brasil, mantenha o nome esperado no `docker-compose.yml`.

## 2. Subir o provider

```powershell
docker-compose up -d osrm
```

## 3. Configurar o projeto

No `.env`:

```dotenv
OSRM_ENABLED=true
OSRM_BASE_URL=http://localhost:5000
OSRM_TIMEOUT_SECONDS=8
```

## 4. Validar

```powershell
python manage.py check
python scripts/analisar_estimativa_pr.py
```

O sistema faz fallback automaticamente quando o provider nao estiver disponivel.
