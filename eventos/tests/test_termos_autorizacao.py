from datetime import date
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse

from cadastros.models import Cargo, Cidade, CombustivelVeiculo, Estado, UnidadeLotacao, Viajante, Veiculo
from eventos.models import Evento, Oficio, TermoAutorizacao
from eventos.services.documentos.renderer import get_termo_autorizacao_template_path


User = get_user_model()


class TermoAutorizacaoModuleTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='termos', password='termos123')
        self.client.login(username='termos', password='termos123')

        self.estado = Estado.objects.create(codigo_ibge='41', nome='Parana', sigla='PR', ativo=True)
        self.cidade = Cidade.objects.create(codigo_ibge='4106902', nome='Curitiba', estado=self.estado, ativo=True)
        self.cargo = Cargo.objects.create(nome='AGENTE')
        self.unidade = UnidadeLotacao.objects.create(nome='UNIDADE TERMOS')
        self.combustivel = CombustivelVeiculo.objects.create(nome='GASOLINA', is_padrao=True)
        self.evento = Evento.objects.create(
            titulo='Evento Termos',
            data_inicio=date(2026, 3, 18),
            data_fim=date(2026, 3, 19),
            cidade_base=self.cidade,
            cidade_principal=self.cidade,
            estado_principal=self.estado,
        )
        self.oficio = Oficio.objects.create(
            evento=self.evento,
            protocolo='123456789',
            data_criacao=date(2026, 3, 10),
            tipo_destino=Oficio.TIPO_DESTINO_INTERIOR,
            status=Oficio.STATUS_RASCUNHO,
        )
        self.veiculo = Veiculo.objects.create(
            placa='ABC1D23',
            modelo='SPIN',
            combustivel=self.combustivel,
            tipo=Veiculo.TIPO_DESCARACTERIZADO,
            status=Veiculo.STATUS_FINALIZADO,
        )
        self.viajante_a = self._criar_viajante('Servidor A', '1234567')
        self.viajante_b = self._criar_viajante('Servidor B', '2345678')
        self.viajante_c = self._criar_viajante('Servidor C', '3456789')

    def _criar_viajante(self, nome, rg):
        return Viajante.objects.create(
            nome=nome,
            status=Viajante.STATUS_FINALIZADO,
            cargo=self.cargo,
            unidade_lotacao=self.unidade,
            cpf=f'52998224{rg[-3:]}',
            telefone=f'4199999{rg[-4:]}',
            rg=rg,
        )

    def test_lista_de_termos_renderiza_no_novo_padrao(self):
        termo = TermoAutorizacao.objects.create(
            evento=self.evento,
            oficio=self.oficio,
            modo_geracao=TermoAutorizacao.MODO_AUTOMATICO_SEM_VIATURA,
            viajante=self.viajante_a,
            destino='Curitiba/PR',
            data_evento=date(2026, 3, 18),
        )

        response = self.client.get(reverse('eventos:documentos-termos'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lista de termos')
        self.assertContains(response, 'oficio-process-card')
        self.assertContains(response, termo.numero_formatado)
        self.assertContains(response, 'Novo termo')

    def test_cria_termo_rapido_e_usa_template_base(self):
        response = self.client.post(
            reverse('eventos:documentos-termos-novo-rapido'),
            {
                'evento': str(self.evento.pk),
                'oficio': str(self.oficio.pk),
                'roteiro': '',
                'destino': 'Londrina/PR',
                'data_evento': '2026-03-18',
                'data_evento_fim': '2026-03-18',
                'texto_complementar': 'Texto rapido',
                'observacoes': 'Obs',
            },
        )

        self.assertEqual(response.status_code, 302)
        termo = TermoAutorizacao.objects.get(modo_geracao=TermoAutorizacao.MODO_RAPIDO)
        self.assertEqual(termo.destino, 'Londrina/PR')
        self.assertEqual(termo.data_evento, date(2026, 3, 18))
        self.assertEqual(
            get_termo_autorizacao_template_path(termo.template_variant).name,
            'termo_autorizacao.docx',
        )

    def test_cria_termos_automaticos_com_viatura_um_por_servidor(self):
        response = self.client.post(
            reverse('eventos:documentos-termos-novo-automatico-com-viatura'),
            {
                'evento': str(self.evento.pk),
                'oficio': str(self.oficio.pk),
                'roteiro': '',
                'destino': 'Maringa/PR',
                'data_evento': '2026-03-18',
                'data_evento_fim': '2026-03-19',
                'texto_complementar': '',
                'observacoes': '',
                'veiculo_id': str(self.veiculo.pk),
                'viajantes_ids': f'{self.viajante_a.pk},{self.viajante_b.pk}',
            },
        )

        self.assertEqual(response.status_code, 302)
        termos = list(TermoAutorizacao.objects.filter(modo_geracao=TermoAutorizacao.MODO_AUTOMATICO_COM_VIATURA).order_by('pk'))
        self.assertEqual(len(termos), 2)
        self.assertTrue(all(termo.veiculo_id == self.veiculo.pk for termo in termos))
        self.assertEqual(len({termo.lote_uuid for termo in termos}), 1)
        self.assertEqual(
            get_termo_autorizacao_template_path(termos[0].template_variant).name,
            'termo_autorizacao_automatico.docx',
        )

    def test_cria_termos_automaticos_sem_viatura_um_por_servidor(self):
        response = self.client.post(
            reverse('eventos:documentos-termos-novo-automatico-sem-viatura'),
            {
                'evento': str(self.evento.pk),
                'oficio': '',
                'roteiro': '',
                'destino': 'Foz do Iguacu/PR',
                'data_evento': '2026-03-18',
                'data_evento_fim': '2026-03-19',
                'texto_complementar': '',
                'observacoes': '',
                'viajantes_ids': f'{self.viajante_a.pk},{self.viajante_b.pk},{self.viajante_c.pk}',
            },
        )

        self.assertEqual(response.status_code, 302)
        termos = list(TermoAutorizacao.objects.filter(modo_geracao=TermoAutorizacao.MODO_AUTOMATICO_SEM_VIATURA).order_by('pk'))
        self.assertEqual(len(termos), 3)
        self.assertTrue(all(not termo.veiculo_id for termo in termos))
        self.assertEqual(
            get_termo_autorizacao_template_path(termos[0].template_variant).name,
            'termo_autorizacao_automatico_sem_viatura.docx',
        )

    def test_autocomplete_de_viajantes_funciona(self):
        response = self.client.get(reverse('eventos:oficio-step1-viajantes-api'), {'q': 'Servidor'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SERVIDOR A')
        self.assertContains(response, 'SERVIDOR B')

    def test_autocomplete_de_viatura_funciona(self):
        response = self.client.get(reverse('eventos:oficio-step2-veiculos-busca-api'), {'q': 'ABC'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ABC1D23')
        self.assertContains(response, 'SPIN')

    def test_validacao_nao_mistura_modo_sem_viatura_com_veiculo(self):
        termo = TermoAutorizacao(
            modo_geracao=TermoAutorizacao.MODO_AUTOMATICO_SEM_VIATURA,
            destino='Curitiba/PR',
            data_evento=date(2026, 3, 18),
            veiculo=self.veiculo,
            servidor_nome='Servidor X',
        )
        with self.assertRaises(ValidationError):
            termo.full_clean()

    def test_downloads_dos_termos_continuam_funcionando(self):
        termo = TermoAutorizacao.objects.create(
            evento=self.evento,
            oficio=self.oficio,
            modo_geracao=TermoAutorizacao.MODO_AUTOMATICO_SEM_VIATURA,
            viajante=self.viajante_a,
            destino='Curitiba/PR',
            data_evento=date(2026, 3, 18),
        )

        response_docx = self.client.get(
            reverse('eventos:documentos-termos-download', kwargs={'pk': termo.pk, 'formato': 'docx'})
        )
        self.assertEqual(response_docx.status_code, 200)
        self.assertEqual(
            response_docx['Content-Type'],
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        )

        with patch('eventos.views_global.convert_docx_bytes_to_pdf_bytes', return_value=b'%PDF-1.4 termo'):
            response_pdf = self.client.get(
                reverse('eventos:documentos-termos-download', kwargs={'pk': termo.pk, 'formato': 'pdf'})
            )
        self.assertEqual(response_pdf.status_code, 200)
        self.assertEqual(response_pdf['Content-Type'], 'application/pdf')
