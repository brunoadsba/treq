"""
Testes unitários para validar Row Level Security (RLS).

Testa apenas a lógica de filtro, sem dependência do Supabase.
"""

import pytest


class TestRLSFilter:
    """Testes unitários para lógica de filtro RLS."""
    
    def _filter_by_rls(self, documents, user_id):
        """
        Replica a lógica de filtro RLS do RAGService.
        Isolado para teste sem dependência externa.
        """
        filtered = []
        
        for doc in documents:
            metadata = doc.get('metadata', {})
            classification = metadata.get('classification', 'internal')
            allowed_users = metadata.get('allowed_users', ['*'])
            
            # Documentos públicos são acessíveis a todos
            if classification == 'public':
                filtered.append(doc)
                continue
            
            # Documentos com "*" são acessíveis a qualquer usuário autenticado
            if '*' in allowed_users:
                filtered.append(doc)
                continue
            
            # Verificar se user_id está na lista de permitidos
            if user_id in allowed_users:
                filtered.append(doc)
                continue
        
        return filtered
    
    def test_public_documents_accessible_to_all(self):
        """Documentos públicos são acessíveis a todos."""
        documents = [
            {"id": "1", "content": "Público", "metadata": {"classification": "public"}},
            {"id": "2", "content": "Interno", "metadata": {"classification": "internal", "allowed_users": ["user_a"]}},
        ]
        
        filtered = self._filter_by_rls(documents, "user_x")
        
        assert len(filtered) == 1
        assert filtered[0]["id"] == "1"
    
    def test_allowed_user_can_access(self):
        """Usuário na lista allowed_users acessa o documento."""
        documents = [
            {"id": "1", "content": "Doc A", "metadata": {"classification": "internal", "allowed_users": ["user_a", "user_b"]}},
        ]
        
        # user_a está na lista
        filtered = self._filter_by_rls(documents, "user_a")
        assert len(filtered) == 1
        
        # user_c NÃO está na lista
        filtered = self._filter_by_rls(documents, "user_c")
        assert len(filtered) == 0
    
    def test_wildcard_allows_all_authenticated(self):
        """Documentos com '*' são acessíveis a qualquer usuário autenticado."""
        documents = [
            {"id": "1", "content": "Para todos", "metadata": {"classification": "internal", "allowed_users": ["*"]}},
        ]
        
        filtered = self._filter_by_rls(documents, "qualquer_usuario")
        assert len(filtered) == 1
    
    def test_confidential_blocked_for_unauthorized(self):
        """Documentos confidenciais são bloqueados para não autorizados."""
        documents = [
            {"id": "1", "content": "Confidencial RH", "metadata": {"classification": "confidential", "allowed_users": ["rh_manager"]}},
        ]
        
        # Não autorizado
        filtered = self._filter_by_rls(documents, "dev_user")
        assert len(filtered) == 0
        
        # Autorizado
        filtered = self._filter_by_rls(documents, "rh_manager")
        assert len(filtered) == 1
    
    def test_mixed_documents_filtering(self):
        """Cenário misto: retorna apenas documentos permitidos."""
        documents = [
            {"id": "1", "content": "Público", "metadata": {"classification": "public"}},
            {"id": "2", "content": "User A", "metadata": {"classification": "internal", "allowed_users": ["user_a"]}},
            {"id": "3", "content": "User B", "metadata": {"classification": "internal", "allowed_users": ["user_b"]}},
            {"id": "4", "content": "Todos", "metadata": {"classification": "internal", "allowed_users": ["*"]}},
            {"id": "5", "content": "Confidencial", "metadata": {"classification": "confidential", "allowed_users": ["admin"]}},
        ]
        
        # User A deve ver: 1 (público), 2 (seu), 4 (wildcard)
        filtered = self._filter_by_rls(documents, "user_a")
        ids = [d["id"] for d in filtered]
        
        assert "1" in ids  # público
        assert "2" in ids  # seu documento
        assert "4" in ids  # wildcard
        assert "3" not in ids  # de user_b
        assert "5" not in ids  # confidencial
        assert len(filtered) == 3
    
    def test_default_allowed_users_is_wildcard(self):
        """Sem allowed_users definido, assume wildcard."""
        documents = [
            {"id": "1", "content": "Sem allowed_users", "metadata": {"classification": "internal"}},
        ]
        
        # Deve acessar pois default é ["*"]
        filtered = self._filter_by_rls(documents, "qualquer")
        assert len(filtered) == 1
