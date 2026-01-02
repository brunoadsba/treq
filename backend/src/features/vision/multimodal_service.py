"""
Serviço Multimodal: Integração com Gemini 1.5 Pro Vision para análise de imagens e documentos.
Localizado em src/features/vision seguindo a arquitetura modular.
"""
import os
import io
import json
import asyncio
from typing import List, Dict, Any, Optional
from PIL import Image
import google.generativeai as genai
from loguru import logger

from app.config import get_settings

settings = get_settings()

class MultimodalService:
    def __init__(self):
        self.api_key = settings.gemini_api_key
        if not self.api_key:
            logger.error("❌ GEMINI_API_KEY não configurada no .env")
            raise ValueError("GEMINI_API_KEY missing")
        
        genai.configure(api_key=self.api_key)
        # Padronizado para 2.5 Flash devido à disponibilidade de quota e performance
        self.model_pro = genai.GenerativeModel('gemini-2.5-flash')
        self.model_flash = genai.GenerativeModel('gemini-2.5-flash')
        
    async def describe_image(self, image_bytes: bytes, prompt: Optional[str] = None) -> str:
        """
        Gera uma descrição semântica detalhada da imagem.
        """
        try:
            img = Image.open(io.BytesIO(image_bytes))
            default_prompt = "Descreva esta imagem em detalhes para um sistema de assistência operacional. Extraia textos visíveis, identifique objetos, máquinas, avisos de segurança e descreva o contexto operacional."
            
            response = await asyncio.to_thread(
                self.model_flash.generate_content,
                [prompt or default_prompt, img]
            )
            return response.text
        except Exception as e:
            logger.error(f"Erro ao descrever imagem: {e}")
            return f"Erro no processamento visual: {str(e)}"

    def _clean_json_text(self, text: str) -> str:
        """Limpa o texto para extrair apenas o conteúdo JSON."""
        text = text.strip()
        # Remover blocos de código markdown
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        
        # Se ainda houver lixo antes/depois do JSON
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
            img = Image.open(io.BytesIO(image_bytes))
            
            prompts = {
                "table": "Extraia todos os dados desta tabela e retorne um objeto JSON válido representando as linhas e colunas. Use chaves claras para os cabeçalhos.",
                "chart": "Analise este gráfico. Extraia os dados numéricos e retorne um JSON formatado com séries, labels e valores.",
                "form": "Extraia os campos preenchidos deste formulário para um objeto JSON chave-valor."
            }
            
            prompt = prompts.get(target_type, prompts["table"])
            prompt += "\nRetorne APENAS o JSON, sem explicações."
            
            response = await asyncio.to_thread(
                self.model_pro.generate_content,
                [prompt, img]
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
        prompt = """
        Analise esta página de documento técnico/operacional da Sotreq.
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
                self.model_pro.generate_content,
                [prompt, img]
            )
            
            clean_text = self._clean_json_text(response.text)
            return json.loads(clean_text)
        except Exception as e:
            logger.error(f"Erro na análise de documento: {e}")
            return {"error": "Falha na análise multimodal", "details": str(e)}

# Instância singleton
multimodal_service = MultimodalService()
