# 🚀 Architecture Analyzer - Hackathon FIAP

Bem-vindo ao **Architecture Analyzer**! Este projeto foi desenvolvido para o Hackathon da FIAP e consiste em uma solução baseada em **Microsserviços**, orientada a eventos e alimentada por Inteligência Artificial (**Gemini 3.1 Pro Preview**) para extrair e diagnosticar componentes, riscos e oferecer recomendações técnicas a partir de diagramas de arquitetura (imagens ou PDFs).

## 🏛️ Arquitetura de Software (SOAT)
Em alinhamento aos requisitos do edital, a solução foi projetada com foco em resiliência, escalabilidade e Clean Architecture.

- **Microsserviços Isolados**: O sistema foi dividido para que cada serviço possua seu próprio ciclo de vida e banco de dados.
  - **API Gateway (`api-gateway`)**: Ponto de entrada síncrono. Cuida do roteamento (BFF).
  - **Upload Service (`upload-service`)**: Persiste arquivos no Azure Blob Storage e envia mensagens para a fila.
  - **Report Service (`report-service`)**: Mantém a persistência final em JSONB isolado no Postgres (`db_reports`).
- **Mensageria Assíncrona**: Utilização de Azure Storage Queue (emulada localmente via Azurite) permitindo o processamento em background (Long Polling) isolando o front do back da IA.
- **Observabilidade**: Grafana e Prometheus configurados, extraindo métricas (`/metrics`) a cada 5s de todos os contêineres.

## 🧠 Inteligência Artificial (IADT)
O componente (`ai-processor`) não é um script isolado, mas sim um microsserviço assíncrono projetado em cima da técnica de Agentic Workflows (com base em conceitos de LangGraph) e LLM Guardrails utilizando **Gemini 3.1 Pro Preview**.

- **Fluxo Agentic & Retry Resiliente**: Implementamos decision-nodes na cadeia da IA. A IA atua como Arquiteto Experto, Auditor DORA e Analista AISecOps. Se o relatório de extração for impreciso e não atingir a aprovação imposta pelas métricas internas (`confidence_score >= 0.4`), a classe acusa instabilidade semântica (alucinação) e dispara um **Retry autônomo** para reavaliar a imagem em novos vetores antes de falhar.
- **Tratamento de Falhas (Fallback)**: Quando esgotado o Retry, o fallback final altera elegantemente o processo da fila para `ERRO` no banco e registra nas métricas locais, sem causar crash de container (Zero Downtime).
- **Guardrails de Schema Estrito (Pydantic)**: Exigido estrutura com validação técnica de Componentes Visíveis, Gargalos/Métricas DORA, Postura de Segurança (SPOFs) e Recomendações *Azure Well-Architected Framework*.

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
- [x] **Fase 2 (Resiliência da Solução)**:
  - **1) Dashboards de Observabilidade**: Subir stack local (Grafana/Prometheus/logs estruturados) consumindo a Telemetria da arquitetura e da IA.
  - **2) Evolução Agentic do Prompt**: Aprimorar foco em Azure Well-Architected Framework, DORA metrics e incluir Retry Agentic Pattern (Tenacity) para inibir alucinações e proteger o parser Pydantic.
- [ ] **Fase 3 (Segurança Avançada e IA)**:
  - **1) LLM-as-a-Judge**: Implementar um segundo nó avaliador rápido na cadeia do LangGraph para validar a recomendação contra alucinações antes da persistência.
  - **2) Defesa contra Prompt Injection**: Incluir nó de sanitização de Input via Visão Computacional (OCR restrito) alertando a esteira sobre envenenamento na imagem ou PDF upado.
  - **3) LangChain / Instructor Estrito**: Refatorar o modelo de Retry manual utilizando `instructor` puro acoplado com classes Pydantic forçando Strict JSON mode no Request pro Gemini.
  - **4) Fila de Mensagens Mortas (DLQ)**: Enviar as mensagens falhas definitivamente da fila padrão (`analyze-queue`) para uma de refugo para análise de segurança sem impactar a fila ativa.
- [ ] **Fase 4 (Entrega Final e Deploy)**: Empacotar ambiente final e rodar os scripts de infraestrutura diretamente na Cloud Azure.
