# Upload Flow Specification

## Visão Geral
Este documento descreve o fluxo de upload arquitetado com Clean Architecture para o Upload Service, incluindo a integração obrigatória com Azure Blob Storage e Azure Storage Queue (utilizando Azurite localmente).

## Fluxo de Execução
1. O `API Gateway` repassa o arquivo (imagem ou PDF) para o `Upload Service` através do endpoint `/internal/upload`.
2. O `Upload Service` recebe a requisição no Controller (`src/main.py`) e aciona o `UploadDiagramUseCase`.
3. O `UploadDiagramUseCase`:
   - Gera um `UUID` único para a análise (`process_id`).
   - Utiliza o `AzureAdapter` para salvar o arquivo físico no **Azure Blob Storage**.
   - Utiliza o `AzureAdapter` para montar e disparar um evento (mensagem JSON) para a **Azure Storage Queue**. O payload inclui o `process_id` e a URL do blob.
   - Retorna a entidade de domínio `UploadRecord` contendo os metadados.
4. O registro do status inicial (`RECEBIDO`) deve ser persistido em banco de dados isolado do serviço de upload (`db_upload`).

## Cobertura de Testes Exigida
O banco de testes em pytest deverá validar cenários onde:
- Blob Storage está inacessível.
- Storage Queue falha na postagem da mensagem.
- Arquivos inválidos são injetados.

Garantir 100% de cobertura nos fluxos de erro do `UploadDiagramUseCase`.