"""
Mock Data Provider para Treq Marketing (EN-US)
Permite busca em base de dados local sem custo de API.
"""

import json
from typing import List, Dict, Any

class MockDataProvider:
    def __init__(self, mock_db_path: str):
        self.path = mock_db_path
        # Simulação de uma base de dados de Marketing Digital
        self.data = [
            {
                "content": "SEO involves optimizing your website to rank higher in search engine results pages.",
                "metadata": {"source": "seo_guide.md", "topic": "SEO", "language": "en"}
            },
            {
                "content": "Content Marketing is a strategic approach focused on creating and distributing valuable content.",
                "metadata": {"source": "content_strategy.md", "topic": "Content", "language": "en"}
            },
            {
                "content": "Email marketing remains one of the most effective ways to nurture leads and drive conversions.",
                "metadata": {"source": "email_marketing.md", "topic": "Email", "language": "en"}
            }
        ]

    async def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Busca simples por palavra-chave para simular RAG."""
        query = query.lower()
        results = []
        for item in self.data:
            if any(word in item["content"].lower() for word in query.split()):
                results.append(item)
        
        return results[:top_k]

# Exemplo de uso no RAGService:
# if mode == "marketing":
#     provider = MockDataProvider("path/to/en/mocks")
#     results = await provider.search(query)
