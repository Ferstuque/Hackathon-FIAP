import logging
from google import genai # Padrão 2026
from google.genai import types
from shared.schemas import TechnicalReport
from src.domain.prompt import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class GeminiAdapter:
    def __init__(self, api_key: str):
        # Novo cliente unificado do Google GenAI
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-3.1-pro-preview"
        
        if not api_key:
            logger.warning("GEMINI_API_KEY ausente. Operando em modo Fallback.")

    async def analyze_architecture(self, image_bytes: bytes, mime_type: str) -> TechnicalReport:
        try:
            # Chamada multimodal moderna com System Instruction nativa
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    "Execute a sua instrução system e retorne os dados apenas como JSON puro."
                ],
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type="application/json"
                )
            )
            
            # Validação Pydantic (Guardrail obrigatório)
            return TechnicalReport.model_validate_json(response.text)
            
        except Exception as e:
            logger.error(f"Erro na extração de arquitetura: {str(e)}")
            return self._get_fallback_report()