Hackathon-FIAP/
├── .github/workflows/          # CI/CD: build, test e deploy
├── .specify/                   # Spec-Kit: Leis e memórias do Agente
│   ├── memory/                 # Schemas Pydantic e regras de negócio
│   ├── templates/              # Boilerplates para novos microserviços
│   └── constitution.md         # Definições globais (Clean Arch, Azure, Segurança)
├── services/                   # Microserviços (cada um com seu Dockerfile)
│   ├── api-gateway/            # FastAPI: BFF e roteamento central
│   ├── upload-service/         # Clean Arch: Recebe arquivos e salva no Blob
│   │   ├── src/
│   │   │   ├── domain/         # Entidades e Interfaces
│   │   │   ├── application/    # Casos de Uso (UploadDiagram)
│   │   │   └── infrastructure/ # Adapters (Postgres, Azure Blob)
│   ├── ai-processor/           # Clean Arch: Consome fila e chama Gemini Flash
│   │   ├── src/
│   │   │   ├── domain/         # Lógica de análise
│   │   │   ├── application/    # Integração Gemini + Pydantic Guardrails
│   │   │   └── infrastructure/ # Adapter para Azure Queue e Gemini API
│   └── report-service/         # Clean Arch: Persiste e entrega o relatório final
├── shared/                     # Código compartilhado (Models Pydantic, Utils de Log)
├── infra/                      # Scripts de auxílio (az cli, scripts SQL iniciais)
├── .env                        # Variáveis de ambiente (não versionar segredos)
├── docker-compose.yml          # Orquestração local (Azurite, Postgres x2, Apps)
└── README.md                   # Documentação obrigatória (Segurança, Arquitetura)