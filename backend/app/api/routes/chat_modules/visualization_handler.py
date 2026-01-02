from typing import Any, Optional, Union
from loguru import logger
import json
from fastapi.responses import StreamingResponse

from .models import ChatRequest, ChatResponse

async def handle_visualization(
    chat_request: ChatRequest,
    visualization_service: Any
) -> Union[StreamingResponse, ChatResponse, None]:
    """
    Processa solicitações de visualização de gráficos.
    Retorna Response (Streaming ou ChatResponse) se gerou gráfico, ou None caso contrário.
    """
    if not (chat_request.visualization and chat_request.action_id):
        return None
        
    logger.info(
        f"[VISUALIZATION] Modo visualização ativado: "
        f"action_id={chat_request.action_id}, "
        f"period={chat_request.context.get('period', 'today') if chat_request.context else 'today'}, "
        f"unit={chat_request.context.get('unit') if chat_request.context else None}"
    )
    
    try:
        chart_data = await visualization_service.generate_chart_data(
            action_id=chat_request.action_id,
            period=chat_request.context.get("period", "today") if chat_request.context else "today",
            unit=chat_request.context.get("unit") if chat_request.context else None
        )
        
        if chart_data:
            logger.info(
                f"[VISUALIZATION] Gráfico gerado com sucesso: "
                f"type={chart_data.get('type')}, "
                f"title={chart_data.get('title')}, "
                f"empty={chart_data.get('metadata', {}).get('empty', False)}"
            )
            
            if chat_request.stream:
                # Streaming: enviar chart_data em um único evento SSE
                def chart_stream():
                    yield f'data: {json.dumps({"chunk": "", "chart_data": chart_data, "done": True})}\n\n'
                
                return StreamingResponse(
                    chart_stream(),
                    media_type="text/event-stream",
                    headers={
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                        "X-Accel-Buffering": "no"
                    }
                )
            else:
                # Não-streaming: retornar ChatResponse com chart_data
                return ChatResponse(
                    response=f"Gráfico: {chart_data['title']}",
                    conversation_id=chat_request.conversation_id,
                    context_summary="",
                    sources=[],
                    chart_data=chart_data
                )
        else:
            logger.warning(
                f"[VISUALIZATION] Falha ao gerar gráfico para {chat_request.action_id}. "
                f"Retornando None - usando fallback texto"
            )
            return None
    except Exception as e:
        logger.error(
            f"[VISUALIZATION] Exceção ao gerar gráfico para {chat_request.action_id}: {e}"
        )
        import traceback
        logger.error(traceback.format_exc())
        return None
