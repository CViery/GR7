import logging
from datetime import datetime
from io import BytesIO

from flask import send_file
from openpyxl import Workbook


logger = logging.getLogger(__name__)


class GerarExcel:
    """Exporta dados sem carregar pandas/numpy na memória da aplicação."""

    def exportar_faturamentos_excel(self, dados):
        if not dados:
            return None

        try:
            workbook = Workbook(write_only=True)
            sheet = workbook.create_sheet('Faturamentos')

            primeiro = dados[0]
            if isinstance(primeiro, dict):
                colunas = list(primeiro.keys())
                sheet.append(colunas)
                for item in dados:
                    sheet.append([item.get(coluna) for coluna in colunas])
            else:
                for item in dados:
                    sheet.append(list(item))

            output = BytesIO()
            workbook.save(output)
            output.seek(0)
            filename = datetime.now().strftime('%Y-%m-%d_%H-%M-%S.xlsx')

            return send_file(
                output,
                download_name=filename,
                as_attachment=True,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        except Exception:
            logger.exception('Erro ao exportar faturamentos para Excel.')
            return None
