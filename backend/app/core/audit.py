from loguru import logger
from datetime import datetime
import json
from typing import Any, Dict, Optional

def log_audit(
    user_id: str,
    action: str,
    resource: str,
    resource_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    success: bool = True
):
    """
    Registra um log de auditoria para fins de conformidade LGPD.
    
    Args:
        user_id (str): ID do usuário que realizou a ação.
        action (str): Descrição da ação (ex: 'UPLOAD_DOCUMENT', 'DELETE_CHAT').
        resource (str): O tipo de recurso afetado (ex: 'DOCUMENT', 'CONVERSATION').
        resource_id (str, optional): ID específico do recurso afetado.
        metadata (dict, optional): Informações adicionais não sensíveis.
        success (bool): Se a ação foi bem-sucedida.
    """
    audit_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": "AUDIT",
        "user_id": user_id,
        "action": action,
        "resource": resource,
        "resource_id": resource_id,
        "success": success,
        "metadata": metadata or {}
    }
    
    # Log estruturado para fácil extração posterior
    logger.bind(audit=True).info(f"AUDIT_TRAIL: {json.dumps(audit_data)}")

def log_mutation(user_id: str, action: str, resource: str, **kwargs):
    """Shortcut para log de mutações bem-sucedidas."""
    log_audit(user_id=user_id, action=action, resource=resource, success=True, **kwargs)

def log_security_event(user_id: str, action: str, **kwargs):
    """Log para eventos de segurança (ex: falha de login, tentativa de acesso negado)."""
    logger.bind(security=True, audit=True).warning(
        f"SECURITY_AUDIT: {json.dumps({'user_id': user_id, 'action': action, **kwargs})}"
    )
