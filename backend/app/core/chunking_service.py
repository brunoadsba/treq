"""
Serviço de chunking semântico para documentos Markdown.
Preserva estrutura hierárquica e evita quebrar procedimentos no meio.
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
from loguru import logger
from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter


class ChunkingService:
    """Serviço para dividir documentos em chunks semânticos."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Inicializa o serviço de chunking.
        
        Args:
            chunk_size: Tamanho máximo do chunk em caracteres
            chunk_overlap: Sobreposição entre chunks em caracteres
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Configurar splitter de Markdown por cabeçalhos
        self.markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "section"),
                ("##", "subsection"),
                ("###", "subsubsection"),
            ]
        )
        
        # Splitter recursivo melhorado: preserva sentenças completas
        # Separadores em ordem de preferência (parágrafos > linhas > sentenças > palavras)
        self.recursive_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " ", ""]
        )
    
    def chunk_markdown(
        self,
        content: str,
        source: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Divide documento Markdown em chunks semânticos preservando estrutura.
        
        Args:
            content: Conteúdo Markdown do documento
            source: Fonte do documento (arquivo, URL, etc.)
            metadata: Metadata adicional para adicionar aos chunks
            
        Returns:
            List[Dict]: Lista de chunks com conteúdo e metadata rica
        """
        try:
            # Dividir por cabeçalhos Markdown
            chunks = self.markdown_splitter.split_text(content)
            
            # Se não houver cabeçalhos, usar splitter recursivo
            if not chunks or len(chunks) == 1:
                logger.warning(f"Documento {source} não tem cabeçalhos Markdown, usando splitter recursivo")
                text_chunks = self.recursive_splitter.split_text(content)
                chunks = [{"page_content": chunk} for chunk in text_chunks]
            
            # Processar chunks e adicionar metadata rica
            processed_chunks = []
            for i, chunk in enumerate(chunks):
                chunk_content = chunk.page_content if hasattr(chunk, 'page_content') else str(chunk)
                
                # Extrair hierarquia de seções do metadata do chunk
                section_hierarchy = []
                chunk_metadata = chunk.metadata if hasattr(chunk, 'metadata') else {}
                
                # Construir hierarquia de seções
                if chunk_metadata.get('section'):
                    section_hierarchy.append(chunk_metadata['section'])
                if chunk_metadata.get('subsection'):
                    section_hierarchy.append(chunk_metadata['subsection'])
                if chunk_metadata.get('subsubsection'):
                    section_hierarchy.append(chunk_metadata['subsubsection'])
                
                # Preparar metadata rica para o chunk
                rich_metadata = {
                    'source': source,
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'section_hierarchy': section_hierarchy,
                    'section': chunk_metadata.get('section', ''),
                    'subsection': chunk_metadata.get('subsection', ''),
                    'subsubsection': chunk_metadata.get('subsubsection', ''),
                }
                
                # Adicionar metadata adicional se fornecida
                if metadata:
                    rich_metadata.update(metadata)
                
                # Fase 2: Enriquecer conteúdo do chunk com contexto
                enriched_content = self._enrich_chunk_content(
                    chunk_content.strip(),
                    source,
                    section_hierarchy,
                    metadata.get('document_type') if metadata else None,
                    i + 1,
                    len(chunks)
                )
                
                processed_chunks.append({
                    'content': enriched_content,
                    'metadata': rich_metadata
                })
            
            logger.info(
                f"Documento {source} dividido em {len(processed_chunks)} chunks "
                f"(preservando {len([c for c in processed_chunks if c['metadata'].get('section_hierarchy')])} seções)"
            )
            
            return processed_chunks
            
        except Exception as e:
            logger.error(f"Erro ao fazer chunking do documento {source}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            
            # Fallback: usar splitter recursivo simples
            logger.info(f"Usando fallback para {source}")
            text_chunks = self.recursive_splitter.split_text(content)
            return [
                {
                    'content': self._enrich_chunk_content(
                        chunk.strip(),
                        source,
                        [],
                        metadata.get('document_type') if metadata else None,
                        i + 1,
                        len(text_chunks)
                    ),
                    'metadata': {
                        'source': source,
                        'chunk_index': i,
                        'total_chunks': len(text_chunks),
                        **({} if not metadata else metadata)
                    }
                }
                for i, chunk in enumerate(text_chunks)
            ]
    
    def chunk_text(
        self,
        content: str,
        source: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Divide texto simples em chunks (sem estrutura Markdown).
        
        Args:
            content: Conteúdo textual
            source: Fonte do documento
            metadata: Metadata adicional
            
        Returns:
            List[Dict]: Lista de chunks com conteúdo e metadata
        """
        try:
            text_chunks = self.recursive_splitter.split_text(content)
            
            return [
                {
                    'content': self._enrich_chunk_content(
                        chunk.strip(),
                        source,
                        [],
                        metadata.get('document_type') if metadata else None,
                        i + 1,
                        len(text_chunks)
                    ),
                    'metadata': {
                        'source': source,
                        'chunk_index': i,
                        'total_chunks': len(text_chunks),
                        **({} if not metadata else metadata)
                    }
                }
                for i, chunk in enumerate(text_chunks)
            ]
        except Exception as e:
            logger.error(f"Erro ao fazer chunking de texto {source}: {e}")
            return []
    
    def _enrich_chunk_content(
        self,
        content: str,
        source: str,
        section_hierarchy: List[str],
        document_type: Optional[str],
        chunk_index: int,
        total_chunks: int
    ) -> str:
        """
        Enriquece conteúdo do chunk com contexto adicional.
        
        Adiciona no início: fonte, seção, tipo e posição no documento.
        Isso ajuda o LLM a entender melhor o contexto de cada chunk.
        
        Args:
            content: Conteúdo original do chunk
            source: Fonte do documento
            section_hierarchy: Hierarquia de seções
            document_type: Tipo do documento
            chunk_index: Índice do chunk (1-based)
            total_chunks: Total de chunks no documento
            
        Returns:
            str: Conteúdo enriquecido
        """
        # Construir cabeçalho contextual
        context_parts = []
        
        # Fonte (apenas nome do arquivo, não caminho completo)
        source_name = Path(source).name if source else "documento"
        context_parts.append(f"Fonte: {source_name}")
        
        # Tipo do documento
        if document_type and document_type != "unknown":
            context_parts.append(f"Tipo: {document_type}")
        
        # Seção hierárquica
        if section_hierarchy:
            section_path = " > ".join(section_hierarchy)
            context_parts.append(f"Seção: {section_path}")
        
        # Posição no documento
        context_parts.append(f"Parte: {chunk_index}/{total_chunks}")
        
        # Montar cabeçalho
        header = " | ".join(context_parts)
        
        # Retornar conteúdo enriquecido (cabeçalho + conteúdo)
        return f"[{header}]\n\n{content}"

