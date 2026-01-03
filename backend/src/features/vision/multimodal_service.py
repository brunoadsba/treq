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

from app.config import get_settings

settings = get_settings()

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

    async def describe_image(self, image_bytes: bytes, prompt: Optional[str] = None) -> str:
        """
        Gera uma descrição semântica detalhada da imagem.
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
            return response.text
        except Exception as e:
            logger.error(f"Erro ao descrever imagem: {e}")
            return f"Erro no processamento visual: {str(e)}"

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
