# Padrões Arquiteturais

## Clean Architecture
Cada microserviço deve ser dividido em:
1. **Domain:** Entidades e regras de negócio puras.
2. **Application:** Casos de uso (Ex: `ProcessUpload`, `GenerateReport`).
3. **Infrastructure/Adapters:** Implementações externas (Repositórios DB, Clientes API, Azure SDKs).

## Comunicação
- **Síncrona:** Gateway -> Services via REST/HTTP.
- **Assíncrona:** Upload Service -> Queue -> AI Processor[cite: 1].