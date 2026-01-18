import os
import socket
from urllib.parse import urlparse, urlunparse
from loguru import logger
from app.config import get_settings

settings = get_settings()

def get_database_url() -> str:
    """
    Resolve a URL do banco de dados com fallback para IPv4 se necessário.
    Útil para ambientes Docker/WSL2 que falham ao resolver IPv6 do Supabase.
    """
    # 1. Tenta pegar DATABASE_URL direta
    db_url = os.getenv("DATABASE_URL") or settings.database_url
    
    if not db_url:
        # Fallback derivado das configurações se possível
        logger.warning("DATABASE_URL não configurada explicitamente. Tentando derivar do Supabase URL.")
        from app.services.vector_health import get_database_url as derive_url
        db_url = derive_url()
        
    if not db_url:
        return ""

    # 2. Lógica de Fallback IPv4 para Supabase
    try:
        parsed = urlparse(db_url)
        hostname = parsed.hostname
        
        # Apenas tenta forçar IPv4 para endereços conhecidos do Supabase que resolvem IPv6
        if hostname and ("supabase.co" in hostname or "supabase.net" in hostname):
            logger.info(f"🔍 Database: Verificando resolução para {hostname}...")
            
            try:
                # 1. Tenta resolução IPv4 padrão
                addr_info = socket.getaddrinfo(hostname, None, socket.AF_INET)
                if addr_info:
                    ipv4 = addr_info[0][4][0]
                    # Se resolveu IP, continua (não muda nada ou usa o IP se quiser)
                else:
                    raise socket.gaierror(-5, "No IPv4 address")
            except (socket.gaierror, Exception):
                logger.warning(f"⚠️ Database: {hostname} não possui IPv4. Tentando Supabase IPv4 Pooler...")
                
                # Extrai o project ref (ex: db.xxxx.supabase.co -> xxxx)
                parts = hostname.split('.')
                project_ref = parts[1] if len(parts) > 1 else ""
                
                if project_ref:
                    # Supabase IPv4 Proxy/Pooler Pattern (Transaction Mode)
                    # User must be "postgres.project_ref"
                    # Port 6543 is often more reliable for IPv4 pooler
                    pooler_host = "aws-0-us-east-1.pooler.supabase.com"
                    new_user = f"postgres.{project_ref}"
                    
                    new_netloc = f"{new_user}:{parsed.password}@{pooler_host}:6543"
                    db_url = urlunparse((
                        parsed.scheme,
                        new_netloc,
                        parsed.path,
                        parsed.params,
                        parsed.query,
                        parsed.fragment
                    ))
                    logger.info(f"✅ Database: Redirecionado para Pooler IPv4 ({pooler_host}:6543)")
                    # logger.debug(f"Redacted URL: {db_url.replace(parsed.password, '****')}")
                
    except Exception as e:
        logger.error(f"❌ Database: Erro crítico ao processar URL: {e}")

    return db_url
