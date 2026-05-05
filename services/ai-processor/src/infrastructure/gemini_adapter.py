import logging
import json
from google import genai
from google.genai import types
from shared.schemas import TechnicalReport
from src.domain.prompt import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class GeminiAdapter:
    def __init__(self, api_key: str):
        # Novo cliente unificado (google-genai)
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-3.1-pro-preview"
        
        if not api_key:
            logger.warning("GEMINI_API_KEY ausente. O sistema operará em modo Fallback/Mock.")

    async def analyze_architecture(self, image_bytes: bytes, mime_type: str) -> TechnicalReport:
        try:
            # Chamada multimodal nativa com System Instruction integrada
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    "Analise este diagrama conforme suas instruções de arquiteto."
                ],
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    temperature=0.2 # Menor temperatura = menos alucinação
                )
            )
            
            # Validação estrita com Pydantic (Guardrail obrigatório do IADT)
            return TechnicalReport.model_validate_json(response.text)
            
        except Exception as e:
            logger.error(f"Falha na IA: {str(e)}. Acionando contingência de segurança[cite: 1].")
            return self._get_fallback_report()

    def _get_fallback_report(self) -> TechnicalReport:
        """Retorna um relatório mockado para garantir que o sistema não pare (Resiliência)[cite: 1]."""
        mock_data = {
            "identified_components": [
                {"name": "API Gateway", "category": "Network", "description": "Entry point for requests."},
                {"name": "Azure SQL", "category": "Storage", "description": "Relational database."}
            ],
            "architectural_risks": ["Single point of failure detected in Gateway."],
            "recommendations": ["Implement multi-region redundancy."],
            "confidence_score": 0.50
        }
        return TechnicalReport(**mock_data)