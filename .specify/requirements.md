# Requisitos Funcionais — Hackathon FIAP

## Serviços Mínimos Obrigatórios
- **API Gateway/BFF:** Ponto de entrada único para o frontend/usuário.
- **Upload Service:** Gerencia arquivos e status inicial.
- **AI Processor:** Realiza a análise via Gemini 3.5 Pro Preview (gemini-3.1-pro-preview).
- **Report Service:** Persiste e serve o relatório técnico final[cite: 1].

## Fluxo de Trabalho
- Upload de diagrama (imagem JPG/PNG ou PDF, máx 10MB)[cite: 1].
- Criação de processo de análise com ID rastreável (UUID).
- Consulta de status: RECEBIDO → PROCESSANDO → ANALISADO → ERRO[cite: 1].
- Relatório técnico: componentes, riscos arquiteturais e recomendações[cite: 1].

## Restrições e Prazos
- MVP funcional em 10 dias.
- Custo Azure: zero ou mínimo (Azurite local; free tiers em cloud).
- Containerização: Docker + Docker Compose[cite: 1].