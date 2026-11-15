import unittest

from app import app


class SmokeTest(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True, SECRET_KEY='test-secret')
        self.client = app.test_client()

    def test_rotas_criticas_registradas(self):
        rotas = {str(regra) for regra in app.url_map.iter_rules()}
        esperadas = {
            '/home', '/gastos', '/cadastros', '/gerencial',
            '/orcamentos/novo', '/api/orcamentos/salvar',
            '/modulos/', '/modulos/orcamentos', '/modulos/vendas',
            '/modulos/clientes', '/modulos/produtos',
            '/modulos/gastos', '/modulos/faturamento',
            '/modulos/relatorios', '/aprovacoes', '/notificacoes',
            '/faturamentos/novo/<int:faturamento_id>/solicitar-edicao',
            '/faturamentos/novo/<int:faturamento_id>/editar',
            '/aprovacoes/<int:solicitacao_id>/decidir'
        }
        self.assertTrue(esperadas.issubset(rotas))

    def test_telas_protegidas_redirecionam_sem_login(self):
        for rota in ('/gerencial', '/gastos', '/cadastros', '/orcamentos/novo'):
            resposta = self.client.get(rota)
            self.assertIn(resposta.status_code, (301, 302), rota)

    def test_modulos_exige_login_e_filial_correta(self):
        resposta = self.client.get('/modulos/')
        self.assertIn(resposta.status_code, (301, 302))

        with self.client.session_transaction() as sessao:
            sessao['usuario'] = 'TESTE'
            sessao['permission'] = 'ADMIN'
            sessao['empresa'] = 1

        resposta = self.client.get('/modulos/')
        self.assertIn(resposta.status_code, (301, 302))

    def test_filial_modulos_abre_dashboard(self):
        with self.client.session_transaction() as sessao:
            sessao['usuario'] = 'TESTE'
            sessao['permission'] = 'ADMIN'
            sessao['empresa'] = 4

        resposta = self.client.get('/home')
        self.assertEqual(resposta.status_code, 302)
        self.assertTrue(resposta.location.endswith('/modulos/'))

    def test_aprovacoes_exige_login(self):
        for rota in ('/aprovacoes', '/notificacoes'):
            resposta = self.client.get(rota)
            self.assertIn(resposta.status_code, (301, 302), rota)


if __name__ == '__main__':
    unittest.main()
