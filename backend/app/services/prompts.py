"""
Prompts específicos por tipo de query para o LLM.
Carrega prompts de arquivos YAML externos para facilitar manutenção e versionamento.
"""
import os
import yaml
from pathlib import Path
from loguru import logger
from typing import Dict

# Diretório base dos prompts
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

# Dicionários globais para armazenar os prompts carregados
SYSTEM_PROMPTS: Dict[str, str] = {}
DEFAULT_PROMPT: str = ""

def load_prompts() -> None:
    """
    Carrega todos os prompts dos arquivos YAML no diretório configurado.
    Atualiza as variáveis globais SYSTEM_PROMPTS e DEFAULT_PROMPT.
    """
    global SYSTEM_PROMPTS, DEFAULT_PROMPT
    
    logger.info(f"Carregando prompts de {PROMPTS_DIR}...")
    
    if not PROMPTS_DIR.exists():
        logger.error(f"Diretório de prompts não encontrado: {PROMPTS_DIR}")
        return

    # Limpar dicionário atual
    SYSTEM_PROMPTS.clear()
    
    # Carregar prompt padrão primeiro
    default_prompt_path = PROMPTS_DIR / "default.yaml"
    if default_prompt_path.exists():
        try:
            with open(default_prompt_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                DEFAULT_PROMPT = data.get("system_prompt", "")
                logger.info("Default prompt carregado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao carregar default prompt: {e}")
            DEFAULT_PROMPT = "Você é um assistente operacional útil." # Fallback mínimo
    else:
        logger.warning("Arquivo default.yaml não encontrado")
        DEFAULT_PROMPT = "Você é um assistente operacional útil."

    # Carregar outros prompts
    for prompt_file in PROMPTS_DIR.glob("*.yaml"):
        if prompt_file.name == "default.yaml":
            continue
            
        try:
            with open(prompt_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                prompt_name = data.get("name")
                system_prompt = data.get("system_prompt")
                
                if prompt_name and system_prompt:
                    SYSTEM_PROMPTS[prompt_name] = system_prompt
                    logger.debug(f"Prompt '{prompt_name}' carregado")
                else:
                    logger.warning(f"Arquivo {prompt_file.name} com formato inválido (missing name or system_prompt)")
                    
        except Exception as e:
            logger.error(f"Erro ao carregar prompt {prompt_file.name}: {e}")

    logger.info(f"Total de {len(SYSTEM_PROMPTS)} prompts específicos carregados")

# Carregar prompts na inicialização do módulo
load_prompts()
