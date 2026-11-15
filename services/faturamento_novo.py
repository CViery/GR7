from datetime import datetime
from decimal import Decimal, InvalidOperation

from database.conection import get_connection


class FaturamentoNovo:
    def __init__(self):
        self.conn = get_connection()

    def disponivel(self):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT CASE WHEN
                OBJECT_ID('dbo.faturamento_novo', 'U') IS NOT NULL
                AND OBJECT_ID('dbo.servicos_catalogo', 'U') IS NOT NULL
                AND OBJECT_ID('dbo.faturamento_servicos', 'U') IS NOT NULL
            THEN 1 ELSE 0 END
            """
        )
        return bool(cursor.fetchone()[0])

    @staticmethod
    def money(value):
        text = str(value or "0").replace("R$", "").replace(" ", "")
        if "," in text:
            text = text.replace(".", "").replace(",", ".")
        try:
            return Decimal(text)
        except InvalidOperation as error:
            raise ValueError(f"Valor inválido: {value}") from error

    @staticmethod
    def integer(value):
        try:
            return int(Decimal(str(value or "0").replace(",", ".")))
        except (InvalidOperation, ValueError) as error:
            raise ValueError(f"Quantidade inválida: {value}") from error

    def _colaborador_id(self, name, filial_id, required=False):
        if not name:
            if required:
                raise ValueError("Selecione o mecânico responsável.")
            return None
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT TOP 1 id FROM dbo.colaboradores
            WHERE filial_id = ? AND UPPER(nome) = UPPER(?)
            """,
            filial_id,
            name,
        )
        row = cursor.fetchone()
        if not row and required:
            raise ValueError(f"Colaborador não encontrado: {name}")
        return int(row[0]) if row else None

    def cadastrar(self, data, usuario_id, filial_id):
        cursor = self.conn.cursor()
        os_number = self.integer(data.get("num_os"))
        cursor.execute(
            "SELECT TOP 1 id FROM dbo.faturamento_novo WHERE filial_id = ? AND num_os = ?",
            filial_id,
            os_number,
        )
        existing = cursor.fetchone()
        if existing:
            return {"duplicado": True, "id": int(existing[0])}

        billing_date = datetime.strptime(data["data_faturamento"], "%Y-%m-%d").date()
        budget_date = datetime.strptime(data["data_orcamento"], "%Y-%m-%d").date()
        mechanic_id = self._colaborador_id(data.get("mecanico"), filial_id, required=True)
        filter_mechanic_id = self._colaborador_id(data.get("filtro_mecanico"), filial_id)

        orcamentista_nome = (data.get("orcamentista") or "").strip() or None
        orcamentista_id = self._colaborador_id(orcamentista_nome, filial_id) if orcamentista_nome else None
        colaborador_id = orcamentista_id or mechanic_id

        aditivo_alias = data.get("aditivo") or data.get("ar_condicionado")
        limpeza_alias = data.get("limpeza_freios") or data.get("funilaria")
        values = {
            key: self.money(data.get(key))
            for key in (
                "pecas", "servicos", "valor_total", "valor_meta", "valor_dinheiro",
                "revitalizacao", "fluido_sangria", "palheta", "detergente_parabrisa",
                "filtro", "pneus", "bateria", "valor_oleo", "freios", "suspensao",
                "injecao_ignicao", "cabecote_motor_arrefecimento", "outros", "oleos",
                "transmissao", "terceiros",
            )
        }
        values["aditivo"] = self.money(aditivo_alias)
        values["limpeza_freios"] = self.money(limpeza_alias)

        try:
            cursor.execute(
                """
                INSERT INTO dbo.faturamento_novo (
                    filial_id, colaborador_id, mecanico_id, mecanico_filtro_id, usuario_id,
                    placa, modelo_veiculo, data_orcamento, data_faturamento,
                    num_os, cia, conversao_pneustore,
                    pecas, servicos, valor_os, valor_meta, valor_dinheiro,
                    revitalizacao, aditivo, quantidade_aditivo, fluido_sangria, palheta,
                    limpeza_freios, detergente_parabrisa, filtro, pneus, bateria,
                    modelo_bateria, quantidade_oleo, valor_oleo, tipo_marca_oleo,
                    freios, suspensao, injecao_ignicao, cabecote_motor_arrefecimento,
                    outros, oleos, transmissao, terceiros, observacoes, orcamentista, criado_em
                ) OUTPUT INSERTED.id VALUES (
                    ?,?,?,?,?, ?,?,?,?,?, ?,?,?,?,?, ?,?,?,?,?, ?,?,?,?,?,
                    ?,?,?,?,?, ?,?,?,?,?, ?,?,?,?,?, ?, SYSUTCDATETIME()
                )
                """,
                filial_id, colaborador_id, mechanic_id, filter_mechanic_id, usuario_id,
                data.get("placa", "").upper().strip(), data.get("modelo_veiculo", "").strip(),
                budget_date, billing_date, os_number, data.get("cia"),
                data.get("conversao_pneustore"), values["pecas"], values["servicos"],
                values["valor_total"], values["valor_meta"], values["valor_dinheiro"],
                values["revitalizacao"], values["aditivo"],
                self.integer(data.get("quantidade_aditivo")), values["fluido_sangria"],
                values["palheta"], values["limpeza_freios"], values["detergente_parabrisa"],
                values["filtro"], values["pneus"], values["bateria"],
                data.get("modelo_bateria"), self.integer(data.get("quantidade_oleo")),
                values["valor_oleo"], data.get("tipo_marca_oleo"), values["freios"],
                values["suspensao"], values["injecao_ignicao"],
                values["cabecote_motor_arrefecimento"], values["outros"], values["oleos"],
                values["transmissao"], values["terceiros"], data.get("obs"), orcamentista_nome,
            )
            faturamento_id = int(cursor.fetchone()[0])
            self._salvar_servicos(cursor, faturamento_id, filial_id, data, values)
            self.conn.commit()
            return {"duplicado": False, "id": faturamento_id}
        except Exception:
            self.conn.rollback()
            raise

    def _salvar_servicos(self, cursor, faturamento_id, filial_id, data, values):
        if filial_id == 2:
            aliases = {
                "AR_CONDICIONADO": (values["aditivo"], 1, ""),
                "LAVAGEM": (values["fluido_sangria"], 1, ""),
                "ALTERNADOR": (values["palheta"], 1, ""),
                "FUNILARIA": (values["limpeza_freios"], 1, ""),
            }
        else:
            aliases = {
                "ADITIVO": (values["aditivo"], self.integer(data.get("quantidade_aditivo")), ""),
                "FLUIDO_SANGRIA": (values["fluido_sangria"], 1, ""),
                "PALHETA": (values["palheta"], 1, ""),
                "LIMPEZA_FREIOS": (values["limpeza_freios"], 1, ""),
                "TERCEIROS": (values["terceiros"], 1, ""),
            }
        items = {
            "REVITALIZACAO": (values["revitalizacao"], 1, ""),
            "DETERGENTE_PARABRISA": (values["detergente_parabrisa"], 1, ""),
            "FILTRO_HIGIENIZACAO": (values["filtro"], 1, ""),
            "PNEUS": (values["pneus"], 1, ""),
            "BATERIA": (values["bateria"], 1, data.get("modelo_bateria") or ""),
            "OLEO": (values["oleos"], self.integer(data.get("quantidade_oleo")), data.get("tipo_marca_oleo") or ""),
            "FREIOS": (values["freios"], 1, ""),
            "SUSPENSAO": (values["suspensao"], 1, ""),
            "INJECAO_IGNICAO": (values["injecao_ignicao"], 1, ""),
            "CABECOTE_MOTOR_ARREFECIMENTO": (values["cabecote_motor_arrefecimento"], 1, ""),
            "OUTROS": (values["outros"], 1, ""),
            "TRANSMISSAO": (values["transmissao"], 1, ""),
            **aliases,
        }
        for code, (total, quantity, detail) in items.items():
            if total == 0 and not detail:
                continue
            cursor.execute("SELECT id FROM dbo.servicos_catalogo WHERE codigo = ?", code)
            service = cursor.fetchone()
            if not service:
                continue
            quantity = Decimal(quantity or 1)
            unit_value = total / quantity if quantity else total
            cursor.execute(
                """
                INSERT INTO dbo.faturamento_servicos
                    (faturamento_id, servico_id, quantidade, valor_unitario, valor_total, detalhe)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                faturamento_id, int(service[0]), quantity, unit_value, total, detail,
            )

    @staticmethod
    def brl(value):
        return f"R$ {Decimal(value or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def listar(self, filial_id, filters=None):
        filters = filters or {}
        conditions = ["f.filial_id = ?"]
        parameters = [filial_id]
        mapping = {
            "data_inicio": ("f.data_faturamento >= ?", filters.get("data_inicio")),
            "data_fim": ("f.data_faturamento <= ?", filters.get("data_fim")),
            "placa": ("f.placa LIKE ?", f"%{filters.get('placa')}%" if filters.get("placa") else None),
            "numero_os": ("f.num_os = ?", filters.get("numero_os")),
            "companhia": ("f.cia = ?", filters.get("companhia")),
        }
        for condition, value in mapping.values():
            if value not in (None, ""):
                conditions.append(condition)
                parameters.append(value)
        if filters.get("mecanico_servico"):
            conditions.append("c.nome = ?")
            parameters.append(filters["mecanico_servico"])

        cursor = self.conn.cursor()
        cursor.execute(
            f"""
            SELECT f.id, f.placa, f.modelo_veiculo, f.data_orcamento,
                   f.data_faturamento, f.dias, f.num_os, f.cia, f.pecas,
                   f.servicos, f.valor_os, f.valor_meta, f.valor_dinheiro,
                   f.observacoes, c.nome AS mecanico
            FROM dbo.faturamento_novo f
            LEFT JOIN dbo.colaboradores c ON c.id = f.mecanico_id
            WHERE {' AND '.join(conditions)}
            ORDER BY f.data_faturamento DESC, f.id DESC
            """,
            *parameters,
        )
        columns = [column[0] for column in cursor.description]
        records = [dict(zip(columns, row)) for row in cursor.fetchall()]
        service_map = self._services_by_faturamento(
            [record["id"] for record in records]
        )
        for record in records:
            record.update(self._services_for_list(
                record["id"], filial_id, service_map.get(record["id"], [])
            ))
            record.update({
                "data_orcamento": record["data_orcamento"].strftime("%d/%m/%Y") if record["data_orcamento"] else "-",
                "data_faturamento": record["data_faturamento"].strftime("%d/%m/%Y") if record["data_faturamento"] else "-",
                "dias_servico": record["dias"], "numero_os": record["num_os"],
                "companhia": record["cia"] or "-", "mecanico_servico": record["mecanico"] or "-",
                "valor_pecas": self.brl(record["pecas"]), "valor_servicos": self.brl(record["servicos"]),
                "total_os": self.brl(record["valor_os"]), "valor_p_meta": self.brl(record["valor_meta"]),
                "valor_em_dinheiro": self.brl(record["valor_dinheiro"]), "obs": record["observacoes"] or "",
                "lts_oleo_motor": 0, "valor_lt_oleo": self.brl(0), "marca_e_tipo_oleo": "",
            })
        return records

    def _services_by_faturamento(self, faturamento_ids):
        if not faturamento_ids:
            return {}
        cursor = self.conn.cursor()
        placeholders = ",".join("?" for _ in faturamento_ids)
        cursor.execute(
            f"""
            SELECT fs.faturamento_id, sc.codigo, fs.valor_total,
                   fs.quantidade, fs.detalhe
            FROM dbo.faturamento_servicos fs
            JOIN dbo.servicos_catalogo sc ON sc.id = fs.servico_id
            WHERE fs.faturamento_id IN ({placeholders})
            """,
            *faturamento_ids,
        )
        result = {}
        for row in cursor.fetchall():
            result.setdefault(int(row[0]), []).append(row[1:])
        return result

    def _services_for_list(self, faturamento_id, filial_id, service_rows=None):
        cursor = self.conn.cursor()
        if service_rows is None:
            cursor.execute(
                """
                SELECT sc.codigo, fs.valor_total, fs.quantidade, fs.detalhe
                FROM dbo.faturamento_servicos fs
                JOIN dbo.servicos_catalogo sc ON sc.id = fs.servico_id
                WHERE fs.faturamento_id = ?
                """,
                faturamento_id,
            )
            service_rows = cursor.fetchall()
        services = {row[0]: row for row in service_rows}
        def amount(code):
            return self.brl(services[code][1] if code in services else 0)
        aliases = (
            ("AR_CONDICIONADO", "LAVAGEM", "ALTERNADOR", "FUNILARIA")
            if filial_id == 2 else
            ("ADITIVO", "FLUIDO_SANGRIA", "PALHETA", "LIMPEZA_FREIOS")
        )
        oil = services.get("OLEO")
        return {
            "valor_revitalizacao": amount("REVITALIZACAO"),
            "valor_aditivo": amount(aliases[0]),
            "valor_fluido_sangria": amount(aliases[1]),
            "valor_palheta": amount(aliases[2]),
            "valor_limpeza_freios": amount(aliases[3]),
            "valor_pastilha_parabrisa": amount("DETERGENTE_PARABRISA"),
            "valor_filtro": amount("FILTRO_HIGIENIZACAO"),
            "valor_pneu": amount("PNEUS"), "valor_bateria": amount("BATERIA"),
            "modelo_bateria": services.get("BATERIA")[3] if "BATERIA" in services else "",
            "lts_oleo_motor": oil[2] if oil else 0,
            "valor_lt_oleo": self.brl((oil[1] / oil[2]) if oil and oil[2] else 0),
            "marca_e_tipo_oleo": oil[3] if oil else "",
        }

    def totais(self, filial_id, filters=None):
        records = self.listar(filial_id, filters)
        total = sum(self.money(item["total_os"]) for item in records)
        target = sum(self.money(item["valor_p_meta"]) for item in records)
        return self.brl(total), self.brl(target)
