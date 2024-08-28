import pandas as pd
from io import BytesIO
from datetime import datetime
from flask import send_file

class GerarExcel:
    def __init__(self):
        pass
    
    def exportar_faturamentos_excel(self, dados):
        try:
            if dados:
                df = pd.DataFrame(dados)
                
                # Cria um buffer em memória para o arquivo Excel
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Faturamentos')
                
                # Posiciona o cursor no início do buffer
                output.seek(0)
                
                # Gera um nome de arquivo com base no timestamp atual
                now = datetime.now()
                filename = now.strftime("%Y-%m-%d_%H-%M-%S") + ".xlsx"
               
                # Retorna o arquivo Excel como uma resposta HTTP
                return send_file(output, attachment_filename=filename, as_attachment=True)
            else:
                print("Nenhum dado foi retornado.")
                return None
        except Exception as e:
            print(f"Erro ao exportar dados para Excel: {e}")
            return None