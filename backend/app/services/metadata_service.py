"""
Serviço de Enriquecimento de Metadados para Sistema RAG
Projeto: Treq - Assistente Operacional Treq

Adiciona campos de metadados para suportar:
- RLS (Row Level Security)
- Filtragem semântica avançada
- Auditoria e versionamento
"""

from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
import re


def detect_document_type(filename: str) -> str:
    """
    Detecta tipo do documento pela extensão.
    
    Args:
        filename: Nome do arquivo
        
    Returns:
        Tipo do documento (markdown, text, pdf, word, unknown)
    """
    ext = Path(filename).suffix.lower()
    
    type_map = {
        '.md': 'markdown',
        '.txt': 'text',
        '.pdf': 'pdf',
        '.docx': 'word',
        '.doc': 'word',
        '.html': 'html',
        '.htm': 'html',
        '.json': 'json',
        '.xml': 'xml',
        '.csv': 'csv'
    }
    
    return type_map.get(ext, 'unknown')


def infer_department(filename: str, content: str) -> str:
    """
    Infere departamento baseado em palavras-chave no nome do arquivo e conteúdo.
    
    Args:
        filename: Nome do arquivo
        content: Conteúdo do documento
        
    Returns:
        Departamento inferido (engenharia, comercial, operacoes, geral)
    """
    filename_lower = filename.lower()
    content_lower = content.lower()[:1000]  # Primeiros 1000 chars
    
    # Palavras-chave por departamento
    keywords_map = {
        'engenharia': [
            'manutencao', 'manutenção', 'engenharia', 'tecnico', 'técnico',
            'equipamento', 'especificacao', 'especificação', 'reparo',
            'diagnostico', 'diagnóstico', 'calibracao', 'calibração'
        ],
        'comercial': [
            'comercial', 'vendas', 'precificacao', 'precificação', 'preco', 'preço',
            'cliente', 'proposta', 'orcamento', 'orçamento', 'contrato',
            'negociacao', 'negociação', 'desconto'
        ],
        'operacoes': [
            'operacional', 'operacao', 'operação', 'procedimento', 'processo',
            'instrucao', 'instrução', 'passo', 'checklist', 'rotina',
            'execucao', 'execução', 'tarefa'
        ],
        'rh': [
            'recursos humanos', 'rh', 'treinamento', 'capacitacao', 'capacitação',
            'colaborador', 'funcionario', 'funcionário', 'admissao', 'admissão'
        ],
        'financeiro': [
            'financeiro', 'contabil', 'contábil', 'fatura', 'pagamento',
            'receita', 'despesa', 'balanco', 'balanço', 'fiscal'
        ]
    }
    
    # Contar matches por departamento
    scores = {}
    for dept, keywords in keywords_map.items():
        score = 0
        for keyword in keywords:
            if keyword in filename_lower:
                score += 3  # Peso maior para nome do arquivo
            if keyword in content_lower:
                score += 1
        scores[dept] = score
    
    # Retornar departamento com maior score
    if scores:
        max_dept = max(scores, key=scores.get)
        if scores[max_dept] > 0:
            return max_dept
    
    return 'geral'


def classify_domain(content: str) -> str:
    """
    Classifica domínio do documento baseado no conteúdo.
    
    Args:
        content: Conteúdo do documento
        
    Returns:
        Domínio classificado (operacional, comercial, tecnico, geral)
    """
    content_lower = content.lower()[:1500]  # Primeiros 1500 chars
    
    # Palavras-chave por domínio
    domain_keywords = {
        'operacional': [
            'procedimento', 'passo', 'instrucao', 'instrução', 'processo',
            'executar', 'realizar', 'verificar', 'checklist', 'rotina'
        ],
        'comercial': [
            'preco', 'preço', 'venda', 'cliente', 'proposta', 'orcamento',
            'orçamento', 'negociacao', 'negociação', 'contrato'
        ],
        'tecnico': [
            'manutencao', 'manutenção', 'equipamento', 'tecnico', 'técnico',
            'especificacao', 'especificação', 'componente', 'sistema',
            'diagnostico', 'diagnóstico'
        ],
        'administrativo': [
            'documento', 'formulario', 'formulário', 'politica', 'política',
            'norma', 'regulamento', 'diretriz'
        ]
    }
    
    # Contar matches por domínio
    scores = {}
    for domain, keywords in domain_keywords.items():
        score = sum(1 for keyword in keywords if keyword in content_lower)
        scores[domain] = score
    
    # Retornar domínio com maior score
    if scores:
        max_domain = max(scores, key=scores.get)
        if scores[max_domain] > 0:
            return max_domain
    
    return 'geral'


def infer_classification(filename: str, content: str, department: str) -> str:
    """
    Infere classificação de sensibilidade do documento.
    
    Args:
        filename: Nome do arquivo
        content: Conteúdo do documento
        department: Departamento do documento
        
    Returns:
        Classificação (public, internal, confidential)
    """
    filename_lower = filename.lower()
    content_lower = content.lower()[:1000]
    
    # Palavras-chave que indicam confidencialidade
    confidential_keywords = [
        'confidencial', 'restrito', 'sigiloso', 'privado', 'secreto',
        'senha', 'credencial', 'financeiro', 'salario', 'salário',
        'contrato', 'acordo', 'nda'
    ]
    
    # Palavras-chave que indicam conteúdo público
    public_keywords = [
        'publico', 'público', 'geral', 'todos', 'comunicado',
        'aviso', 'informativo'
    ]
    
    # Verificar palavras-chave de confidencialidade
    has_confidential = any(kw in filename_lower or kw in content_lower 
                          for kw in confidential_keywords)
    
    # Verificar palavras-chave de público
    has_public = any(kw in filename_lower or kw in content_lower 
                    for kw in public_keywords)
    
    if has_confidential:
        return 'confidential'
    elif has_public:
        return 'public'
    else:
        # Padrão mais restritivo
        return 'internal'


def extract_keywords(content: str, max_keywords: int = 10) -> List[str]:
    """
    Extrai palavras-chave principais do conteúdo.
    
    Args:
        content: Conteúdo do documento
        max_keywords: Número máximo de keywords
        
    Returns:
        Lista de palavras-chave
    """
    # Remover pontuação e converter para minúsculas
    words = re.findall(r'\b[a-záàâãéèêíïóôõöúçñ]{4,}\b', content.lower())
    
    # Stopwords em português (simplificado)
    stopwords = {
        'para', 'com', 'por', 'que', 'como', 'quando', 'onde', 'qual',
        'quais', 'este', 'esta', 'esse', 'essa', 'aquele', 'aquela',
        'seu', 'sua', 'seus', 'suas', 'nosso', 'nossa', 'nossos', 'nossas',
        'dele', 'dela', 'deles', 'delas', 'mais', 'menos', 'muito', 'pouco',
        'todo', 'toda', 'todos', 'todas', 'outro', 'outra', 'outros', 'outras',
        'mesmo', 'mesma', 'mesmos', 'mesmas', 'também', 'ainda', 'sobre',
        'após', 'antes', 'durante', 'entre', 'sem', 'sob', 'sobre'
    }
    
    # Filtrar stopwords
    words = [w for w in words if w not in stopwords]
    
    # Contar frequência
    word_freq = {}
    for word in words:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # Ordenar por frequência e retornar top N
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    
    return [word for word, freq in sorted_words[:max_keywords]]


def prepare_metadata(
    filename: str,
    content: str,
    user_id: Optional[str] = None,
    chunk_index: int = 0,
    total_chunks: int = 1,
    custom_metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Prepara metadados enriquecidos para indexação.
    
    Args:
        filename: Nome do arquivo
        content: Conteúdo do documento (ou chunk)
        user_id: ID do usuário proprietário (opcional)
        chunk_index: Índice do chunk atual
        total_chunks: Total de chunks do documento
        custom_metadata: Metadados customizados adicionais
        
    Returns:
        Dicionário com metadados completos
    """
    # Inferir informações do documento
    document_type = detect_document_type(filename)
    department = infer_department(filename, content)
    domain = classify_domain(content)
    classification = infer_classification(filename, content, department)
    keywords = extract_keywords(content)
    
    # Metadados base
    metadata = {
        # Campos existentes (compatibilidade)
        "filename": filename,
        "source": Path(filename).stem,
        "document_type": document_type,
        "file_size": len(content),
        "chunk_index": chunk_index,
        "total_chunks": total_chunks,
        
        # CORRIGIDO: Campos para RLS (SEGURO)
        "allowed_users": _get_secure_allowed_users(user_id, classification),
        "department": department,
        "classification": classification,
        
        # NOVOS: Campos para filtragem semântica
        "domain": domain,
        "keywords": keywords,
        
        # NOVOS: Campos de auditoria
        "indexed_at": datetime.utcnow().isoformat(),
        "version": "1.0",
        
        # Campos calculados
        "relative_path": str(Path(filename)),
        "is_complete_document": total_chunks == 1,
        "chunk_position": "start" if chunk_index == 0 else "end" if chunk_index == total_chunks - 1 else "middle"
    }
    
    # Adicionar metadados customizados
    if custom_metadata:
        metadata.update(custom_metadata)
    
    # VALIDAÇÃO FINAL DE SEGURANÇA
    _validate_security_metadata(metadata)
    
    return metadata


def _get_secure_allowed_users(user_id: Optional[str], classification: str) -> List[str]:
    """Determina allowed_users de forma segura baseado na classificação."""
    # REGRA CRÍTICA: Documentos confidenciais NUNCA podem ser públicos
    if classification in ['confidential', 'restricted']:
        if not user_id:
            raise SecurityError(f"Confidential documents require explicit user_id. Classification: {classification}")
        return [user_id]
    
    # Documentos internos: usuário específico ou anonymous se não fornecido
    if classification == 'internal':
        return [user_id] if user_id else ["anonymous"]
    
    # Apenas documentos públicos podem usar "*"
    if classification == 'public':
        return ["*"]
    
    # Default: usuário específico ou anonymous
    return [user_id] if user_id else ["anonymous"]


def _validate_security_metadata(metadata: Dict[str, Any]) -> None:
    """Validação de segurança obrigatória antes da indexação."""
    classification = metadata.get('classification')
    allowed_users = metadata.get('allowed_users', [])
    
    # REGRA 1: Documentos confidenciais NUNCA podem ser públicos
    if classification in ['confidential', 'restricted'] and '*' in allowed_users:
        raise SecurityError(f"SECURITY VIOLATION: Confidential documents cannot have public access (*). Classification: {classification}")
    
    # REGRA 2: allowed_users não pode estar vazio
    if not allowed_users:
        raise SecurityError("SECURITY VIOLATION: allowed_users cannot be empty - RLS requirement")
    
    # REGRA 3: Validar formato de user_id
    for user in allowed_users:
        if user not in ['*', 'anonymous'] and not isinstance(user, str):
            raise SecurityError(f"SECURITY VIOLATION: Invalid user_id format: {user}")


class SecurityError(Exception):
    """Exceção para violações de segurança em metadados."""
    pass


def validate_metadata(metadata: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Valida se metadados possuem todos os campos obrigatórios.
    
    Args:
        metadata: Dicionário de metadados
        
    Returns:
        Tupla (is_valid, list_of_errors)
    """
    required_fields = [
        "filename", "source", "document_type", "allowed_users",
        "department", "classification", "domain", "indexed_at"
    ]
    
    errors = []
    
    for field in required_fields:
        if field not in metadata:
            errors.append(f"Campo obrigatório ausente: {field}")
        elif metadata[field] is None:
            errors.append(f"Campo obrigatório é None: {field}")
        elif isinstance(metadata[field], str) and not metadata[field].strip():
            errors.append(f"Campo obrigatório está vazio: {field}")
    
    # Validações específicas
    if "allowed_users" in metadata:
        if not isinstance(metadata["allowed_users"], list):
            errors.append("Campo 'allowed_users' deve ser uma lista")
        elif len(metadata["allowed_users"]) == 0:
            errors.append("Campo 'allowed_users' não pode ser lista vazia")
    
    if "classification" in metadata:
        valid_classifications = ["public", "internal", "confidential"]
        if metadata["classification"] not in valid_classifications:
            errors.append(f"Classificação inválida: {metadata['classification']}")
    
    return len(errors) == 0, errors


# Exemplo de uso
if __name__ == "__main__":
    sample_filename = "procedimento_manutencao_equipamento_x.md"
    sample_content = """
# Procedimento de Manutenção do Equipamento X

## Objetivo
Este documento descreve o procedimento padrão para manutenção preventiva
do equipamento X, utilizado nas operações de campo.

## Etapas
1. Verificar nível de óleo hidráulico
2. Inspecionar componentes elétricos
3. Testar sistema de freios
4. Realizar ajustes necessários

## Responsável
Departamento de Engenharia
"""
    
    print("=== Teste de Enriquecimento de Metadados ===\n")
    
    # Preparar metadados
    metadata = prepare_metadata(
        filename=sample_filename,
        content=sample_content,
        user_id="user_eng_001",
        chunk_index=0,
        total_chunks=1
    )
    
    print("Metadados Gerados:")
    for key, value in metadata.items():
        print(f"  {key}: {value}")
    
    # Validar metadados
    is_valid, errors = validate_metadata(metadata)
    print(f"\n=== Validação ===")
    print(f"Válido: {is_valid}")
    if errors:
        print("Erros encontrados:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✅ Todos os campos obrigatórios presentes!")
