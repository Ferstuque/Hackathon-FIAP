# 🚀 Architecture Analyzer - Hackathon FIAP

Bem-vindo ao **Architecture Analyzer**! Este projeto foi desenvolvido para o Hackathon da FIAP e consiste em uma solução baseada em **Microsserviços**, orientada a eventos e alimentada por Inteligência Artificial (**Gemini 3.1 Pro Preview**) para extrair e diagnosticar componentes, riscos e oferecer recomendações técnicas a partir de diagramas de arquitetura (imagens ou PDFs).

## 🏛️ Arquitetura e Padrões
A aplicação foi construída com base em **Clean Architecture** (separando Domain, Application e Infrastructure) e desenhada como uma arquitetura de microsserviços totalmente isolados.

- **API Gateway (`api-gateway`)**: Ponto de entrada síncrono. Cuida do roteamento, validação primária de formato e exposição das respostas finais sem tocar em bancos de dados de estado.
- **Upload Service (`upload-service`)**: Microsserviço responsável por receber o artefato, persistir no Azure Blob Storage e lançar uma mensagem assíncrona na Azure Storage Queue alertando que há trabalho a ser feito. (Seu banco de dados mapeia o status).
- **AI Processor (`ai-processor`)**: Um worker que roda em background em *Long Polling* extraindo mensagens da fila, processando de forma multimodal no LLM com *System Prompt* robusto baseado na técnica de Guardrails.
- **Report Service (`report-service`)**: Persiste o json final mapeado em banco num repositório inteiramente à parte (`db_reports`).

## 🛠️ Stack Tecnológica

- **Linguagem**: Python 3.14
- **Framework Web**: FastAPI (totalmente assíncrono)
- **Mensageria/Storage**: Azure Storage Queue / Azure Blob Storage (Azurite localmente para custo zero e emulação fidedigna)
- **Bancos de Dados**: PostgreSQL com asyncpg & SQLAlchemy (Databases isolados por serviço)
- **IA**: Google Gemini 3.1 Pro Preview (via *google-generativeai*)
- **Containers**: Docker & Docker Compose
- **Testes / CI**: Pytest, Pytest-Asyncio e cobertura garantida pelo Github Actions.

## ⚙️ Pré-requisitos e Execução (Custo Zero)

1. Você precisará ter o **Docker** e o **Docker Compose** instalados na sua máquina.
2. Na raiz do repositório, crie um arquivo `.env` (ou utilize variáveis de ambiente exportadas) provendo a sua chave do Gemini:
   ```env
   GEMINI_API_KEY=sua_secret_key_aqui
   ```
3. Suba toda a infraestrutura através do Docker Compose:
   ```bash
   docker-compose up --build -d
   ```
Isso irá levantar o **Azurite** (Emulador Azure), 2 bancos **Postgres**, e os **4 microsserviços**.

## 🔌 API Endpoints Principais

As requisições partem do **API Gateway**, mapeado em `http://localhost:8000`:

* **`POST /api/v1/upload`**
  - **Payload**: `multipart/form-data` (Envie chave `file` com sua Imagem JPG, PNG ou PDF da arquitetura).
  - **Retorna**: Um Payload constando o `id` (UUID gerado para seu processo) e status `RECEBIDO`.
* **`GET /api/v1/status/{analysis_id}`**
  - **Path Parameter**: O seu UUID do arquivo enviado.
  - **Retornar**: Status do processamento (`PROCESSANDO`, `ANALISADO`, `ERRO`).
* **`GET /api/v1/report/{analysis_id}`**
  - **Retorno**: Extrato estruturado JSON preenchido pelo IA detalhando:
      - `identified_components` (componentes do diagrama e categorias)
      - `architectural_risks`
      - `recommendations`
      - `confidence_score`

## 🧪 Testes de Resiliência

Foi aplicada uma suíte focada em falhas e observabilidade (exigência do edital). Para rodar os testes via compose:
```bash
# Rodando a suíte de testes isolados do Upload-Service
docker-compose exec upload-service pytest --cov=src tests/ --cov-report=term-missing
```

Os testes são executados automaticamente através do GitHub Actions, comprovando a eficácia e entrega do requisito CI/CD do Hackathon.

## 🗺️ Estratégia e Desdobramento (Roadmap)

Nossa arquitetura e ciclo de vida seguem a diretriz **"Local-First to Cloud-Native"**. Toda a engenharia, integração e validação são feitas e provadas primeiro no ambiente local (utilizando containers Docker, emuladores como Azurite para Azure Storage e mocks de IA controlados), garantindo zero surpresas e custo zero. Logo após a validação bem-sucedida do pipeline E2E, a estrutura é provisionada e **escalada nativamente na Azure Cloud**, conectando aos recursos gerenciados oficiais.

### 📍 Planejamento de Execução Atual
- [x] **Fase 1 (Base e Integração E2E)**: Comunicação assíncrona validada, com CI/CD, banco de dados JSONB e conectores isolados fechados com sucesso.
- [ ] **Fase 2 (Resiliência e Visibilidade)**:
  - **1) Dashboards de Observabilidade**: Subir stack local (Grafana/Prometheus/logs estruturados) consumindo a Telemetria e métricas de Performance da IA (Concluído).
  - **2) Evolução do Prompt de IA**: Aprimorar o foco nos pilares do Azure Well-Architected Framework, DORA metrics e incluir Retry Agentic Pattern com base em `tenacity` e métricas de confiança da IA (Concluído).
  - **3) Resiliência com Filas de Mensagens Mortas**: Garantia de reprocessamento implementando DLQ (Dead Letter Queue) no Azure Storage Queue.
- [ ] **Fase 3-4 (Refinamento Avançado)**: Polimento dos Guardrails Pydantic validando rigidamente o Gemini 3.1 Pro Preview, além do fine-tuning antes do deploy oficial na Azure Cloud.
