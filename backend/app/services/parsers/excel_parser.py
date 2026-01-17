import pandas as pd
from io import BytesIO
from typing import Dict, Any
from .base_parser import BaseParser
from loguru import logger

class ExcelParser(BaseParser):
    def parse(self, file_content: bytes, file_name: str) -> Dict[str, Any]:
        logger.info(f"Iniciando parse de Planilha: {file_name}")
        try:
            is_csv = file_name.lower().endswith('.csv')
            
            if is_csv:
                df = pd.read_csv(BytesIO(file_content))
                sheets = {"Sheet1": df}
            else:
                # Ler todas as abas
                sheets = pd.read_excel(BytesIO(file_content), sheet_name=None)
            
            markdown_parts = []
            total_rows = 0
            
            for sheet_name, df in sheets.items():
                if df.empty:
                    continue
                
                # Converter para Markdown
                markdown = df.to_markdown(index=False)
                markdown_parts.append(f"### Planilha: {sheet_name}\n\n{markdown}")
                total_rows += len(df)
            
            result_content = "\n\n".join(markdown_parts)
            
            metadata = {
                "sheet_count": len(sheets),
                "total_rows": total_rows,
                "file_type": "CSV" if is_csv else "Excel"
            }
            
            return self._create_result(result_content, metadata)
            
        except Exception as e:
            logger.error(f"Erro ao parsear Planilha {file_name}: {str(e)}")
            raise ValueError(f"Falha ao processar Planilha: {str(e)}")
