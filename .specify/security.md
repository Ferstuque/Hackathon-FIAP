# Estratégia de Segurança

## Proteção de Dados e IA
- **Validação de Payload:** Rejeição de arquivos com extensões não permitidas ou scripts embutidos[cite: 1].
- **AI Guardrails:** Validação estrita da saída da LLM via Pydantic para mitigar alucinações[cite: 1].
- **Limitação de Escopo:** O sistema deve ignorar prompts que não sejam relacionados à arquitetura de software.

## Infraestrutura Segura
- **Secrets:** Uso de variáveis de ambiente (.env) e segredos do GitHub Actions (nunca hardcoded).
- **Tratamento de Erros:** Logs não devem expor chaves de API ou strings de conexão[cite: 1].