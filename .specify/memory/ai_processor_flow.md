# Fluxo do AI Processor

## Responsabilidades
- **Consumo:** Escutar a `analysis-queue` (Azure Storage Queue).
- **Status:** Notificar o Upload Service para mudar status para `PROCESSANDO`.
- **Multimodalidade:** Baixar o diagrama do Blob Storage e enviar para o Gemini 2.5 Flash.
- **Validação:** Aplicar o schema Pydantic `TechnicalReport` na saída da IA.
- **Persistência:** Enviar o relatório final para o Report Service.

## Estratégia de Erro
- Em caso de falha na IA, a mensagem deve voltar para a fila (Retry) ou ser marcada como `ERRO` após 3 tentativas.