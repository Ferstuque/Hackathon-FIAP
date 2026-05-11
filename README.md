# FIAP Secure Systems: Architecture AI Analyzer 🚀

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![React](https://img.shields.io/badge/React-v19-purple)
![FastAPI](https://img.shields.io/badge/FastAPI-v0.110-green)
![Gemini](https://img.shields.io/badge/AI-Gemini_3.1_Pro-orange)

## 📌 1. O Problema
Empresas que operam sistemas distribuídos possuem dezenas de diagramas de arquitetura, muitas vezes analisados visualmente e manualmente em busca de vulnerabilidades, pontos únicos de falha e boas práticas. Esse processo **não escala**, demanda muito tempo de especialistas caros (Arquitetos/Staff Engineers) e é propenso a falhas humanas. 

Para resolver isso, construímos o **FIAP Secure Systems AI Analyzer**, uma ferramenta que aplica IA Multimodal (Visão + Linguagem) para processar diagramas de arquitetura em segundos, emitindo pareceres técnicos estruturados sobre Componentes, Riscos e Recomendações.

---

## 🏛️ 2. Arquitetura Proposta e Fluxo da Solução

O sistema foi desenhado aplicando **Arquitetura Baseada em Microsserviços** (Clean Architecture/Hexagonal em cada serviço) com um fluxo altamente desacoplado e **Assíncrono**.

### Diagrama de Arquitetura (O Nosso Sistema)

\\\mermaid
graph TD
    Client[👩‍💻 React Frontend] -->|HTTP POST| API[🚪 API Gateway / BFF]
    API -->|Encaminha| UPL[📤 Upload Service]
    
    UPL -->|1. Salva| Blob[(🪣 Azure Blob Storage)]
    UPL -->|2. Mensagem| Queue[[📨 Azure Storage Queue]]
    
    Queue -->|Consome Polling| AI[🤖 AI Processor Worker]
    Blob -.->|Lê Imagem| AI
    
    AI <-->|Prompt + Imagem| Gemini[🧠 Gemini 3.1 VLM]
    AI -->|Grava JSON| REP[📄 Report Service]
    REP -->|Persiste| DB[(🐘 DB PostgreSQL)]
    
    Client -.->|Polling GET Status & Report| API
    API -.-> REP
\\\

### Fluxo da Solução
1. **Upload**: O cliente acessa a interface React e envia um diagrama (PNG, JPG, PDF).
2. **Ingestão**: O \API Gateway\ recebe e joga para o \Upload Service\.
3. **Assincronismo**: O Upload Service salva o arquivo no \Blob Storage\, posta um evento na \Fila (Queue)\ e devolve um Status HTTP 202 (Accepted). 
4. **Processamento (IADT)**: O \AI Processor\ (rodando em background) pega a mensagem da Fila, converte o diagrama, aplica *Prompt Engineering* no Gemini Vision e aguarda o parecer.
5. **Persistência**: O JSON estruturado do modelo é enviado ao \Report Service\ e gravado num banco de dados isolado.
6. **Frontend Updates (SSE/Polling)**: O frontend consulta o \API Gateway\ até o status virar \ANALISADO\, renderizando então o relatório técnico em tela.

---

## 🚀 3. Instruções de Execução

Requisitos: Docker e Docker Compose instalados.

1. Clone o repositório.
2. Crie na raiz um arquivo \.env\ e defina \GEMINI_API_KEY=sua_chave\.
3. Suba os containers locais:
\\\ash
docker compose up --build -d
\\\
4. Acesse:
   - **Frontend**: \http://localhost:5173\ (Se rodar via Vite localmente: \cd frontend && npm run dev\)
   - **API Gateway**: \http://localhost:8000/docs\
   - **Métricas Prometheus**: \http://localhost:9090\

*(Para o deploy Cloud-Native na Azure, configuramos um GitHub Actions workflow base no diretório .github/workflows/deploy.yml provisionando infraestrutura moderna Serverless usando Azure Container Apps via Bicep).*

---

## 🛡️ 4. Segurança (Seção Obrigatória)

Aplicamos rigorosas práticas defensivas tanto a nível de arquitetura quanto na IA:

1. **Estratégias de Validação e Tratamento de Entradas:**
   - **Frontend & Backend**: Restrição rígida de MIME Types (aceitando estritamente imagens e PDF).
   - Bloqueio de injeção de payload em metadados. Limite de tamanho de arquivo.

2. **Uso Controlado de Modelos de IA (Guardrails e Limites):**
   - Utilizamos *Prompt Engineering* fortemente tipado (forçando resposta restrita ou diretivas explícitas) limitando as saídas e escopo do LLM estritamente à análise arquitetural técnica.
   - **Mitigação de Alucinação (Hallucination)**: Configuramos *Zero Temperature (T=0.1)* para as chamadas da IA limitando a criatividade e aumentando o determinismo focado na topologia da imagem.

3. **Tratamento Seguro de Falhas (AI Exceptions):**
   - Caso a API da IA caia, de timeout, ou viole o formato, o \AI Processor\ captura a exceção de forma segura, aciona uma \Dead Letter Queue (DLQ)\ e atualiza o processo para status \ERRO\ sem vazar a stacktrace interna para o usuário.

4. **Isolamento e Práticas na Comunicação:**
   - **Segurança de Rede**: Serviços internos não possuem portas expostas diretamente para a internet. Só recebem comunicação via rede privada Docker/Kubernetes.
   - Apenas o \API Gateway\ está exposto para recebimento das chamadas (atuando como Edge router).

5. **Riscos e Limitações Catalogados:**
   - *Limitação do VLM (Vision Model)*: Em diagramas extremamente densos ou com fontes muito pequenas, a IA pode omitir um microsserviço ou sub-rede.
   - *Risco de Context Window*: O modelo possui um cap; topologias de altíssima escala corporativa terão recomendada a subdivisão do diagrama antes do envio.

---
*Hackathon Integrado FIAP (IADT + SOAT) 2026*
