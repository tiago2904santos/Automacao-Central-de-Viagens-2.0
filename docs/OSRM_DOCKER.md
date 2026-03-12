# OSRM local com Docker (Windows)

Rode o OSRM em Docker Desktop no Windows para usar rota real na estimativa de viagem (em vez do fallback Haversine).

## Pré-requisitos

- **Docker Desktop** para Windows instalado e em execução.
- Espaço em disco: ~2–3 GB para o mapa do Brasil.

## 1. Preparar o mapa (uma vez)

Crie a pasta e baixe o mapa OSM do Brasil (Geofabrik):

```powershell
mkdir -p data/osrm
cd data/osrm
# Baixar Brasil (ou use Paraná para menos espaço: https://download.geofabrik.de/south-america/brazil/sul-latest.osm.pbf)
Invoke-WebRequest -Uri "https://download.geofabrik.de/south-america/brazil-latest.osm.pbf" -OutFile "brazil-latest.osm.pbf"
```

Processar o mapa com OSRM (extract, partition, customize):

```powershell
# Na pasta do projeto (raiz)
docker run -t -v "${PWD}/data/osrm:/data" ghcr.io/project-osrm/osrm-backend:latest osrm-extract -p /opt/car.lua /data/brazil-latest.osm.pbf
docker run -t -v "${PWD}/data/osrm:/data" ghcr.io/project-osrm/osrm-backend:latest osrm-partition /data/brazil-latest.osrm
docker run -t -v "${PWD}/data/osrm:/data" ghcr.io/project-osrm/osrm-backend:latest osrm-customize /data/brazil-latest.osrm
```

No PowerShell antigo (sem `${PWD}`):

```powershell
$dir = (Get-Location).Path
docker run -t -v "${dir}/data/osrm:/data" ghcr.io/project-osrm/osrm-backend:latest osrm-extract -p /opt/car.lua /data/brazil-latest.osm.pbf
docker run -t -v "${dir}/data/osrm:/data" ghcr.io/project-osrm/osrm-backend:latest osrm-partition /data/brazil-latest.osrm
docker run -t -v "${dir}/data/osrm:/data" ghcr.io/project-osrm/osrm-backend:latest osrm-customize /data/brazil-latest.osrm
```

## 2. Subir o OSRM

Na raiz do projeto:

```powershell
docker-compose up -d osrm
```

Aguarde o container iniciar (alguns segundos). Teste:

```powershell
curl "http://localhost:5000/route/v1/driving/-49.27,-25.43;-51.93,-23.42?overview=false"
```

## 3. Ligar no Django

No `.env` (ou variáveis de ambiente):

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `OSRM_ENABLED` | Ativa uso do OSRM como fonte principal | `true` ou `false` |
| `OSRM_BASE_URL` | URL do serviço OSRM (route) | `http://localhost:5000` |
| `OSRM_TIMEOUT_SECONDS` | Timeout da requisição HTTP (1–30 s) | `5` |

Exemplo:

```
OSRM_ENABLED=true
OSRM_BASE_URL=http://localhost:5000
OSRM_TIMEOUT_SECONDS=5
```

Reinicie a aplicação. As estimativas passarão a usar OSRM quando disponível (`rota_fonte=OSRM`, `fallback_usado=False`). Se o OSRM estiver fora ou der timeout, o sistema usa o fallback automaticamente (`fallback_usado=True`).

## 4. Parar

```powershell
docker-compose stop osrm
```

Para desativar OSRM sem parar o container: `OSRM_ENABLED=false` no `.env`.
