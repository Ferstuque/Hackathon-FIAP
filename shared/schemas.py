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
        description="Lista de componentes identificados (ex: Compute, Database, Observability)"
    )
    architectural_risks: list[str] = Field(
        description="Possíveis riscos: segurança, escalabilidade (DORA), pontos únicos de falha ou falta de resiliência"
    )
    recommendations: list[str] = Field(
        description="Sugestões técnicas e de governança focadas em Azure Well-Architected e AISecOps"
    )
    security_posture: str | None = Field(
        default=None, description="Avaliação da postura de segurança, acessibilidade e isolamento (Network/WAF)"
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