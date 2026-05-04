from enum import Enum
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

# --- ENUMS ---

class AnalysisStatus(str, Enum):
    """Estados do processo exigidos pelo edital."""
    RECEBIDO = "RECEBIDO"
    PROCESSANDO = "PROCESSANDO"
    ANALISADO = "ANALISADO"
    ERRO = "ERRO"

# --- IA OUTPUT SCHEMAS (Guardrails) ---

class ArchitectureComponent(BaseModel):
    """Representa um componente identificado no diagrama."""
    name: str = Field(description="Nome do componente (ex: Load Balancer, Azure SQL)")
    category: str = Field(description="Categoria (Compute, Storage, Network, Security)")
    description: str | None = Field(default=None, description="Função curta do componente no fluxo")

class TechnicalReport(BaseModel):
    """O schema que o Gemini deve preencher obrigatoriamente."""
    model_config = ConfigDict(populate_by_name=True)

    identified_components: list[ArchitectureComponent] = Field(
        description="Lista de componentes identificados na imagem ou PDF"
    )
    architectural_risks: list[str] = Field(
        description="Possíveis riscos de segurança, escalabilidade ou pontos únicos de falha"
    )
    recommendations: list[str] = Field(
        description="Sugestões técnicas e melhorias baseadas em boas práticas"
    )
    confidence_score: float = Field(
        ge=0, le=1, description="Grau de confiança da IA na análise do diagrama"
    )

# --- SERVICE SCHEMAS ---

class AnalysisProcess(BaseModel):
    """Registro completo do processo para persistência nos bancos de dados."""
    id: UUID
    filename: str
    status: AnalysisStatus
    created_at: datetime
    updated_at: datetime
    # O relatório só existirá após o status ser 'ANALISADO'
    report: TechnicalReport | None = None