# Infraestrutura e DevOps

## Local (Docker Compose)
- **Azurite:** Emulador de Blob Storage (porta 10000) e Queues (porta 10001).
- **PostgreSQL 1 (db_upload):** Porta 5432 - Exclusivo do Upload Service[cite: 1].
- **PostgreSQL 2 (db_report):** Porta 5433 - Exclusivo do Report Service[cite: 1].
- **Network:** Bridge network interna para comunicação entre microserviços.

## Cloud (Azure)
- **Azure Container Apps:** Hospedagem serverless (escala a zero).
- **Azure Storage Account:** LRS (Locally Redundant Storage) para baixo custo.
- **Azure Database for PostgreSQL:** Flexible Server (Burstable tier).

## CI/CD (GitHub Actions)
- Pipeline automatizado com estágios de Build e Test[cite: 1].
- Deploy automatizado para Azure via login por Service Principal.