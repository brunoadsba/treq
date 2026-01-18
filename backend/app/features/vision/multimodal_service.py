"""
Serviço Multimodal: Integração com o novo Google GenAI SDK para análise de imagens e documentos.
Localizado em src/features/vision seguindo a arquitetura modular.
"""
import io
import json
import asyncio
from typing import List, Dict, Any, Optional
from PIL import Image
from google import genai
from loguru import logger
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception, before_sleep_log

from app.config import get_settings

settings = get_settings()

class MultimodalError(Exception):
    """Exceção base para erros no serviço multimodal."""
    pass

class MultimodalQuotaError(MultimodalError):
    """Exceção para erros de cota/rate limit."""
    pass

class MultimodalService:
    def __init__(self):
        self.api_key = settings.gemini_api_key
        self._client = None
        
        if not self.api_key:
            logger.warning("⚠️ GEMINI_API_KEY não configurada. Funcionalidades de visão estarão limitadas.")
        else:
            try:
                self._client = genai.Client(api_key=self.api_key)
                logger.info("✅ Cliente Gemini Vision (google-genai) inicializado com sucesso.")
            except Exception as e:
                logger.error(f"❌ Erro ao inicializar cliente Gemini Vision: {e}")

    def _get_client(self):
        if not self._client:
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY missing. Configure no .env")
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    @retry(
        wait=wait_exponential(multiplier=2, min=4, max=20),
        stop=stop_after_attempt(3),
        retry=retry_if_exception(lambda e: "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e) or "quota" in str(e).lower()),
        before_sleep=before_sleep_log(logger, "WARNING"),
        reraise=True
    )
    async def describe_image(self, image_bytes: bytes, prompt: Optional[str] = None) -> str:
        """
        Gera uma descrição semântica detalhada da imagem com retentativa para quota.
        """
        try:
            client = self._get_client()
            img = Image.open(io.BytesIO(image_bytes))
            
            default_prompt = "Descreva esta imagem em detalhes para um sistema de assistência operacional. Extraia textos visíveis, identifique objetos, máquinas, avisos de segurança e descreva o contexto operacional."
            
            # O novo SDK google-genai lida com PIL Images diretamente
            response = await asyncio.to_thread(
                client.models.generate_content,
                model='gemini-2.0-flash',
                contents=[prompt or default_prompt, img]
            )
            
            if not response or not response.text:
                raise MultimodalError("Resposta vazia do Gemini Vision")
                
            return response.text
        except Exception as e:
            # Se for 429, o retry vai cuidar. Se esgotar tentativas, cai aqui.
            error_msg = str(e)
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                logger.error(f"Quota Gemini excedida persistentemente: {e}")
                raise MultimodalQuotaError("Limite de uso do serviço de visão atingido.")
            
            logger.error(f"Erro ao descrever imagem: {e}")
            raise MultimodalError(f"Falha no processamento visual: {error_msg}")

    def _clean_json_text(self, text: str) -> str:
        """Limpa o texto para extrair apenas o conteúdo JSON."""
        text = text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            text = text[start:end+1]
            
        return text

    @retry(
        wait=wait_exponential(multiplier=2, min=4, max=20),
        stop=stop_after_attempt(3),
        retry=retry_if_exception(lambda e: "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e)),
        before_sleep=before_sleep_log(logger, "WARNING"),
        reraise=True
    )
    async def extract_structured_data(self, image_bytes: bytes, target_type: str = "table") -> Dict[str, Any]:
        """
        Extrai dados estruturados (tabelas ou gráficos) no formato JSON.
        """
        try:
            client = self._get_client()
            img = Image.open(io.BytesIO(image_bytes))
            
            prompts = {
                "table": "Extraia todos os dados desta tabela e retorne um objeto JSON válido representando as linhas e colunas. Use chaves claras para os cabeçalhos.",
                "chart": "Analise este gráfico. Extraia os dados numéricos e retorne um JSON formatado com séries, labels e valores.",
                "form": "Extraia os campos preenchidos deste formulário para um objeto JSON chave-valor."
            }
            
            prompt = prompts.get(target_type, prompts["table"])
            prompt += "\nRetorne APENAS o JSON, sem explicações."
            
            response = await asyncio.to_thread(
                client.models.generate_content,
                model='gemini-2.0-flash',
                contents=[prompt, img]
            )
            
            clean_text = self._clean_json_text(response.text)
            return json.loads(clean_text)
        except Exception as e:
            logger.error(f"Erro na extração estruturada ({target_type}): {e}")
            return {"success": False, "error": str(e)}

    @retry(
        wait=wait_exponential(multiplier=2, min=4, max=20),
        stop=stop_after_attempt(3),
        retry=retry_if_exception(lambda e: "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e)),
        before_sleep=before_sleep_log(logger, "WARNING"),
        reraise=True
    )
    async def comprehensive_analysis(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Realiza análise completa (descrição + estruturado) em uma única chamada para economizar cota.
        """
        client = self._get_client()
        prompt = """
        Realize uma análise técnica completa desta imagem/documento operacional.
        Retorne um JSON com a seguinte estrutura:
        {
          "description": "Descrição detalhada da cena, objetos, máquinas e avisos de segurança",
          "summary": "Resumo executivo do conteúdo técnico/procedimento",
          "tables": [], 
          "charts": "Descrição de tendências e dados visuais se houver",
          "alerts": ["Lista de pontos de atenção, erros ou riscos detectados"]
        }
        Retorne APENAS o JSON válido.
        """
        try:
            img = Image.open(io.BytesIO(image_bytes))
            response = await asyncio.to_thread(
                client.models.generate_content,
                model='gemini-2.0-flash',
                contents=[prompt, img]
            )
            
            clean_text = self._clean_json_text(response.text)
            return json.loads(clean_text)
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                 raise MultimodalQuotaError("Limite de cota atingido")
            logger.error(f"Erro na análise completa: {e}")
            raise MultimodalError(f"Falha na análise multimodal: {error_msg}")

    @retry(
        wait=wait_exponential(multiplier=2, min=4, max=20),
        stop=stop_after_attempt(3),
        retry=retry_if_exception(lambda e: "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e)),
        before_sleep=before_sleep_log(logger, "WARNING"),
        reraise=True
    )
    async def analyze_document_page(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Análise completa de uma página de documento (texto + tabelas + insights).
        """
        client = self._get_client()
        prompt = """
        Analise esta página de documento técnico/operacional.
        Identifique e extraia em um JSON estruturado:
        1. "summary": Um resumo executivo do que trata o documento.
        2. "tables": Uma lista de objetos onde cada objeto é uma tabela encontrada (lista de dicts).
        3. "charts": Descrição de gráficos e tendências se houver.
        4. "alerts": Lista de avisos, erros, picos ou pontos de atenção detectados.
        
        Retorne APENAS o JSON válido.
        """
        try:
            img = Image.open(io.BytesIO(image_bytes))
            response = await asyncio.to_thread(
                client.models.generate_content,
                model='gemini-2.0-flash',
                contents=[prompt, img]
            )
            
            clean_text = self._clean_json_text(response.text)
            return json.loads(clean_text)
        except Exception as e:
            logger.error(f"Erro na análise de documento: {e}")
            return {"error": "Falha na análise multimodal", "details": str(e)}

# Instância singleton
multimodal_service = MultimodalService()
