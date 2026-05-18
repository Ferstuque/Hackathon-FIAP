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
    AGUARDANDO_REVISAO_HUMANA = "AGUARDANDO_REVISAO_HUMANA"
    ERRO = "ERRO"

# --- IA OUTPUT SCHEMAS (Guardrails) ---

class ArchitectureComponent(BaseModel):
    """Representa um componente identificado no diagrama."""
    name: str = Field(description="Nome do componente (ex: Load Balancer, Azure SQL)")
    category: str = Field(description="Categoria (Compute, Storage, Network, Security)")
    description: str | None = Field(default=None, description="Função curta do componente no fluxo")

class ArchitecturalRisk(BaseModel):
    risk: str = Field(description="O risco arquitetural identificado")
    severity: str = Field(description="Nível de Severidade: Alta, Média, Baixa")
    affected_components: list[str] = Field(description="Componentes afetados pelo risco")

class ActionableRecommendation(BaseModel):
    recommendation: str = Field(description="Recomendação para mitigar o risco")
    framework: str = Field(description="Framework de mercado associado (ex: Azure Well-Architected Framework, DORA, Zero-Trust)")
    effort: str = Field(description="Esforço Estimado para implementar: Alto, Médio, Baixo")

class ObservabilityMetrics(BaseModel):
    processing_time_ms: float = Field(description="Tempo de processamento (ms)")
    llm_model: str = Field(description="Qual modelo foi usado")
    token_in: int = Field(description="Quantidade de tokens de entrada")
    token_out: int = Field(description="Quantidade de tokens de saída")

class TechnicalReport(BaseModel):
    """O schema que o Gemini deve preencher obrigatoriamente."""
    model_config = ConfigDict(populate_by_name=True)

    identified_components: list[ArchitectureComponent] = Field(
        description="Lista de componentes identificados (ex: Compute, Database, Observability)"
    )
    architectural_risks: list[ArchitecturalRisk] = Field(
        description="Possíveis riscos: segurança, escalabilidade (DORA), pontos únicos de falha ou falta de resiliência classificados com severidade"
    )
    recommendations: list[ActionableRecommendation] = Field(
        description="Sugestões técnicas e de governança focadas em Azure Well-Architected e AISecOps com frameworks sugeridos e esforço"
    )
    security_posture: str | None = Field(
        default=None, description="Avaliação da postura de segurança, acessibilidade e isolamento (Network/WAF)"
    )
    confidence_score: float = Field(
        ge=0, le=1, description="Grau de confiança da IA na análise do diagrama"
    )
    observability: ObservabilityMetrics | None = Field(
        default=None, description="Métricas de tempo e tokens consumidos"
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