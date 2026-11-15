import json
import logging
import os
import smtplib
from datetime import datetime, timezone
from email.message import EmailMessage

from database.conection import get_connection


logger = logging.getLogger(__name__)


class AprovacoesEdicao:
    DURACAO_MINUTOS = 30

    def __init__(self):
        self.conn = get_connection()

    @staticmethod
    def _dict(cursor, row):
        if not row:
            return None
        return {column[0]: value for column, value in zip(cursor.description, row)}

    def obter_faturamento(self, faturamento_id, filial_id):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT id, filial_id, num_os, placa, modelo_veiculo,
                   data_orcamento, data_faturamento, pecas, servicos,
                   valor_os, valor_meta, valor_dinheiro, observacoes
            FROM dbo.faturamento_novo
            WHERE id = ? AND filial_id = ?
            """,
            faturamento_id,
            filial_id,
        )
        return self._dict(cursor, cursor.fetchone())

    def obter_servicos_faturamento(self, faturamento_id, filial_id):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT sf.servico_id, sf.nome_exibicao, sc.aceita_quantidade,
                   sc.aceita_detalhe, COALESCE(fs.quantidade, 0) AS quantidade,
                   COALESCE(fs.valor_total, 0) AS valor_total,
                   COALESCE(fs.detalhe, '') AS detalhe
            FROM dbo.servicos_filiais sf
            JOIN dbo.servicos_catalogo sc ON sc.id = sf.servico_id
            LEFT JOIN dbo.faturamento_servicos fs
              ON fs.servico_id = sf.servico_id AND fs.faturamento_id = ?
            WHERE sf.filial_id = ? AND sf.ativo = 1 AND sc.ativo = 1
            ORDER BY sf.ordem_exibicao, sf.id
            """,
            faturamento_id,
            filial_id,
        )
        return [self._dict(cursor, row) for row in cursor.fetchall()]

    def _aprovadores(self, filial_id):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT DISTINCT u.id, u.usuario, u.email, ae.recebe_email
            FROM dbo.aprovadores_edicao ae
            JOIN dbo.usuarios u ON u.id = ae.usuario_id
            WHERE ae.ativo = 1 AND u.ativo = 1
              AND (ae.filial_id = ? OR ae.filial_id IS NULL)
            """,
            filial_id,
        )
        rows = [self._dict(cursor, row) for row in cursor.fetchall()]
        if rows:
            return rows

        # Compatibilidade inicial: até os aprovadores serem configurados,
        # administradores de guia global recebem a solicitação interna.
        cursor.execute(
            """
            SELECT id, usuario, email, CAST(1 AS bit) AS recebe_email
            FROM dbo.usuarios
            WHERE perfil = 'ADMIN' AND guia = 0 AND ativo = 1
            """
        )
        return [self._dict(cursor, row) for row in cursor.fetchall()]

    def solicitar(self, faturamento_id, filial_id, solicitante_id, motivo, campos):
        faturamento = self.obter_faturamento(faturamento_id, filial_id)
        if not faturamento:
            raise ValueError("OS não encontrada nesta filial.")
        if not motivo or len(motivo.strip()) < 10:
            raise ValueError("Informe um motivo com pelo menos 10 caracteres.")
        valid_fields = {
            "identificacao", "datas", "valores", "pagamento",
            "observacoes", "servicos_adicionais",
        }
        campos = [field for field in campos if field in valid_fields]
        if not campos:
            raise ValueError("Selecione ao menos um campo que deseja alterar.")

        cursor = self.conn.cursor()
        cursor.execute("SELECT usuario FROM dbo.usuarios WHERE id = ?", solicitante_id)
        requester_row = cursor.fetchone()
        requester_name = requester_row[0] if requester_row else "Um usuário"
        cursor.execute(
            """
            SELECT TOP 1 id, campos_solicitados
            FROM dbo.solicitacoes_edicao
            WHERE faturamento_id = ? AND solicitante_id = ?
              AND status IN ('PENDENTE', 'APROVADA')
              AND (liberado_ate IS NULL OR liberado_ate > SYSUTCDATETIME())
            ORDER BY solicitado_em DESC
            """,
            faturamento_id,
            solicitante_id,
        )
        existing = cursor.fetchone()
        if existing:
            raise ValueError("Já existe uma solicitação ativa para esta OS.")

        cursor.execute(
            """
            INSERT INTO dbo.solicitacoes_edicao
                (faturamento_id, filial_id, solicitante_id, motivo, campos_solicitados)
            OUTPUT INSERTED.id
            VALUES (?, ?, ?, ?, ?)
            """,
            faturamento_id,
            filial_id,
            solicitante_id,
            motivo.strip(),
            json.dumps(campos, ensure_ascii=False),
        )
        solicitacao_id = int(cursor.fetchone()[0])
        aprovadores = self._aprovadores(filial_id)

        for aprovador in aprovadores:
            cursor.execute(
                """
                INSERT INTO dbo.notificacoes (usuario_id, tipo, titulo, mensagem, url)
                VALUES (?, 'SOLICITACAO_EDICAO', ?, ?, ?)
                """,
                aprovador["id"],
                f"Solicitação para alterar OS {faturamento['num_os']}",
                f"{requester_name} solicitou autorização para editar a OS {faturamento['num_os']}.",
                f"/aprovacoes/{solicitacao_id}",
            )
        self.conn.commit()
        self._enviar_emails(
            aprovadores, solicitacao_id, faturamento, motivo, requester_name
        )
        return solicitacao_id

    def _enviar_emails(
        self, aprovadores, solicitacao_id, faturamento, motivo, requester_name
    ):
        host = os.getenv("SMTP_HOST")
        sender = os.getenv("SMTP_FROM")
        if not host or not sender:
            return
        recipients = [
            item["email"] for item in aprovadores
            if item.get("email") and item.get("recebe_email")
        ]
        if not recipients:
            return

        base_url = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:5000").rstrip("/")
        message = EmailMessage()
        message["Subject"] = f"GR7 - autorização para editar OS {faturamento['num_os']}"
        message["From"] = sender
        message["To"] = ", ".join(recipients)
        message.set_content(
            f"{requester_name} solicitou uma edição na OS "
            f"{faturamento['num_os']}.\n\n"
            f"Motivo: {motivo.strip()}\n\n"
            f"Analise dentro do GR7: {base_url}/aprovacoes/{solicitacao_id}\n\n"
            "Por segurança, a decisão exige login de administrador."
        )
        try:
            port = int(os.getenv("SMTP_PORT", "587"))
            with smtplib.SMTP(host, port, timeout=10) as smtp:
                if os.getenv("SMTP_TLS", "1") == "1":
                    smtp.starttls()
                username = os.getenv("SMTP_USER")
                password = os.getenv("SMTP_PASSWORD")
                if username and password:
                    smtp.login(username, password)
                smtp.send_message(message)
        except Exception:
            # A notificação interna já foi gravada; falha de e-mail não cancela
            # a solicitação e pode ser acompanhada no log.
            logger.exception("Não foi possível enviar o e-mail de aprovação.")

    def obter_solicitacao(self, solicitacao_id):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT s.*, f.num_os, f.placa, f.modelo_veiculo,
                   u.usuario AS solicitante,
                   d.usuario AS aprovador
            FROM dbo.solicitacoes_edicao s
            JOIN dbo.faturamento_novo f ON f.id = s.faturamento_id
            JOIN dbo.usuarios u ON u.id = s.solicitante_id
            LEFT JOIN dbo.usuarios d ON d.id = s.decidido_por
            WHERE s.id = ?
            """,
            solicitacao_id,
        )
        return self._dict(cursor, cursor.fetchone())

    def pode_aprovar(self, usuario_id, filial_id):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT TOP 1 1
            FROM dbo.aprovadores_edicao
            WHERE usuario_id = ? AND ativo = 1
              AND (filial_id = ? OR filial_id IS NULL)
            """,
            usuario_id,
            filial_id,
        )
        if cursor.fetchone():
            return True
        cursor.execute(
            """
            SELECT TOP 1 1 FROM dbo.usuarios
            WHERE id = ? AND perfil = 'ADMIN' AND guia = 0 AND ativo = 1
            """,
            usuario_id,
        )
        return cursor.fetchone() is not None

    def listar(self, usuario_id, permission):
        cursor = self.conn.cursor()
        if permission == "ADMIN":
            cursor.execute(
                """
                SELECT TOP 200 s.id, s.status, s.solicitado_em, s.liberado_ate,
                       f.num_os, f.placa, u.usuario AS solicitante, s.motivo
                FROM dbo.solicitacoes_edicao s
                JOIN dbo.faturamento_novo f ON f.id = s.faturamento_id
                JOIN dbo.usuarios u ON u.id = s.solicitante_id
                ORDER BY CASE WHEN s.status = 'PENDENTE' THEN 0 ELSE 1 END,
                         s.solicitado_em DESC
                """
            )
        else:
            cursor.execute(
                """
                SELECT TOP 200 s.id, s.status, s.solicitado_em, s.liberado_ate,
                       f.num_os, f.placa, u.usuario AS solicitante, s.motivo
                FROM dbo.solicitacoes_edicao s
                JOIN dbo.faturamento_novo f ON f.id = s.faturamento_id
                JOIN dbo.usuarios u ON u.id = s.solicitante_id
                WHERE s.solicitante_id = ?
                ORDER BY s.solicitado_em DESC
                """,
                usuario_id,
            )
        return [self._dict(cursor, row) for row in cursor.fetchall()]

    def decidir(self, solicitacao_id, aprovador_id, aprovado, justificativa):
        solicitacao = self.obter_solicitacao(solicitacao_id)
        if not solicitacao or solicitacao["status"] != "PENDENTE":
            raise ValueError("Esta solicitação já foi decidida ou não existe.")
        if solicitacao["solicitante_id"] == aprovador_id:
            raise ValueError("O solicitante não pode aprovar a própria edição.")
        status = "APROVADA" if aprovado else "RECUSADA"
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE dbo.solicitacoes_edicao
            SET status = ?, decidido_por = ?, decidido_em = SYSUTCDATETIME(),
                justificativa_decisao = ?,
                liberado_ate = CASE WHEN ? = 'APROVADA'
                    THEN DATEADD(MINUTE, ?, SYSUTCDATETIME()) ELSE NULL END
            WHERE id = ? AND status = 'PENDENTE'
            """,
            status,
            aprovador_id,
            (justificativa or "").strip(),
            status,
            self.DURACAO_MINUTOS,
            solicitacao_id,
        )
        cursor.execute(
            """
            INSERT INTO dbo.notificacoes (usuario_id, tipo, titulo, mensagem, url)
            VALUES (?, 'DECISAO_EDICAO', ?, ?, ?)
            """,
            solicitacao["solicitante_id"],
            f"Solicitação {status.lower()}",
            f"A solicitação da OS {solicitacao['num_os']} foi {status.lower()}.",
            f"/aprovacoes/{solicitacao_id}",
        )
        self.conn.commit()
        self._enviar_decisao_email(solicitacao, status, justificativa)

    def _enviar_decisao_email(self, solicitacao, status, justificativa):
        host = os.getenv("SMTP_HOST")
        sender = os.getenv("SMTP_FROM")
        if not host or not sender:
            return
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT email FROM dbo.usuarios WHERE id = ?",
            solicitacao["solicitante_id"],
        )
        row = cursor.fetchone()
        if not row or not row[0]:
            return
        base_url = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:5000").rstrip("/")
        message = EmailMessage()
        message["Subject"] = (
            f"GR7 - solicitação {status.lower()} para OS {solicitacao['num_os']}"
        )
        message["From"] = sender
        message["To"] = row[0]
        message.set_content(
            f"Sua solicitação para editar a OS {solicitacao['num_os']} foi "
            f"{status.lower()}.\n\nResposta: {justificativa or '-'}\n\n"
            f"Acesse: {base_url}/aprovacoes/{solicitacao['id']}"
        )
        try:
            port = int(os.getenv("SMTP_PORT", "587"))
            with smtplib.SMTP(host, port, timeout=10) as smtp:
                if os.getenv("SMTP_TLS", "1") == "1":
                    smtp.starttls()
                username = os.getenv("SMTP_USER")
                password = os.getenv("SMTP_PASSWORD")
                if username and password:
                    smtp.login(username, password)
                smtp.send_message(message)
        except Exception:
            logger.exception("Não foi possível enviar a devolutiva por e-mail.")

    def autorizacao_ativa(self, faturamento_id, usuario_id):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE dbo.solicitacoes_edicao
            SET status = 'EXPIRADA'
            WHERE status = 'APROVADA' AND liberado_ate <= SYSUTCDATETIME()
            """
        )
        cursor.execute(
            """
            SELECT TOP 1 id, campos_solicitados
            FROM dbo.solicitacoes_edicao
            WHERE faturamento_id = ? AND solicitante_id = ?
              AND status = 'APROVADA' AND utilizado_em IS NULL
              AND liberado_ate > SYSUTCDATETIME()
            ORDER BY decidido_em DESC
            """,
            faturamento_id,
            usuario_id,
        )
        row = cursor.fetchone()
        self.conn.commit()
        if not row:
            return None
        try:
            fields = json.loads(row[1] or "[]")
        except (TypeError, json.JSONDecodeError):
            fields = []
        return {"id": int(row[0]), "campos": fields}

    def salvar_edicao(self, faturamento_id, filial_id, usuario_id, dados):
        authorization = self.autorizacao_ativa(faturamento_id, usuario_id)
        if not authorization:
            raise PermissionError("A autorização expirou ou já foi utilizada.")
        solicitacao_id = authorization["id"]

        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT placa, modelo_veiculo, data_orcamento, data_faturamento,
                   pecas, servicos, valor_os, valor_dinheiro, observacoes
            FROM dbo.faturamento_novo WITH (UPDLOCK, ROWLOCK)
            WHERE id = ? AND filial_id = ?
            """,
            faturamento_id,
            filial_id,
        )
        before = self._dict(cursor, cursor.fetchone())
        if not before:
            raise ValueError("OS não encontrada.")
        before["servicos_adicionais"] = self.obter_servicos_faturamento(
            faturamento_id, filial_id
        )

        field_groups = {
            "identificacao": {"placa", "modelo_veiculo"},
            "datas": {"data_orcamento", "data_faturamento"},
            "valores": {"pecas", "servicos", "valor_os"},
            "pagamento": {"valor_dinheiro"},
            "observacoes": {"observacoes"},
        }
        allowed = set()
        for group in authorization["campos"]:
            allowed.update(field_groups.get(group, set()))
        if not allowed and "servicos_adicionais" not in authorization["campos"]:
            raise PermissionError("A autorização não contém campos editáveis.")
        after = dict(before)
        for key in allowed:
            after[key] = dados.get(key)
        cursor.execute(
            """
            UPDATE dbo.faturamento_novo
            SET placa = ?, modelo_veiculo = ?, data_orcamento = ?, data_faturamento = ?,
                pecas = ?, servicos = ?, valor_os = ?, valor_dinheiro = ?, observacoes = ?
            WHERE id = ? AND filial_id = ?
            """,
            after["placa"], after["modelo_veiculo"], after["data_orcamento"],
            after["data_faturamento"], after["pecas"], after["servicos"],
            after["valor_os"], after["valor_dinheiro"], after["observacoes"],
            faturamento_id, filial_id,
        )
        if "servicos_adicionais" in authorization["campos"]:
            services_after = []
            for item in dados.get("_servicos", []):
                unit_value = (
                    item["valor_total"] / item["quantidade"]
                    if item["quantidade"] else item["valor_total"]
                )
                cursor.execute(
                    """
                    MERGE dbo.faturamento_servicos AS target
                    USING (SELECT ? AS faturamento_id, ? AS servico_id) AS source
                    ON target.faturamento_id = source.faturamento_id
                       AND target.servico_id = source.servico_id
                    WHEN MATCHED THEN UPDATE SET
                        quantidade = ?, valor_unitario = ?, valor_total = ?, detalhe = ?
                    WHEN NOT MATCHED THEN INSERT
                        (faturamento_id, servico_id, quantidade, valor_unitario, valor_total, detalhe)
                    VALUES (?, ?, ?, ?, ?, ?);
                    """,
                    faturamento_id, item["servico_id"],
                    item["quantidade"], unit_value, item["valor_total"], item["detalhe"],
                    faturamento_id, item["servico_id"], item["quantidade"],
                    unit_value, item["valor_total"], item["detalhe"],
                )
                services_after.append(item)
            after["servicos_adicionais"] = services_after
        cursor.execute(
            """
            INSERT INTO dbo.auditoria_faturamento
                (faturamento_id, solicitacao_id, usuario_id, filial_id,
                 dados_anteriores, dados_novos)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            faturamento_id, solicitacao_id, usuario_id, filial_id,
            json.dumps(before, ensure_ascii=False, default=str),
            json.dumps(after, ensure_ascii=False, default=str),
        )
        cursor.execute(
            """
            UPDATE dbo.solicitacoes_edicao
            SET status = 'UTILIZADA', utilizado_em = SYSUTCDATETIME()
            WHERE id = ? AND status = 'APROVADA'
            """,
            solicitacao_id,
        )
        self.conn.commit()

    def notificacoes(self, usuario_id):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE dbo.notificacoes
            SET lida_em = SYSUTCDATETIME()
            WHERE usuario_id = ? AND lida_em IS NULL
            """,
            usuario_id,
        )
        cursor.execute(
            """
            SELECT TOP 50 id, tipo, titulo, mensagem, url, lida_em, criada_em
            FROM dbo.notificacoes
            WHERE usuario_id = ?
            ORDER BY criada_em DESC
            """,
            usuario_id,
        )
        result = [self._dict(cursor, row) for row in cursor.fetchall()]
        self.conn.commit()
        return result
