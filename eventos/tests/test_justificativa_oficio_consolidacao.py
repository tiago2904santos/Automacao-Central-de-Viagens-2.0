from datetime import date

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import Client, TestCase
from django.urls import reverse

from eventos.models import DocumentoAvulso, Evento, Justificativa, ModeloJustificativa, Oficio
from eventos.services.documentos.context import build_justificativa_document_context


User = get_user_model()


class JustificativaOficioConsolidacaoTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='just1x1', password='just1x1')
        self.client.login(username='just1x1', password='just1x1')

        self.evento = Evento.objects.create(
            titulo='Evento consolidacao justificativa',
            data_inicio=date(2026, 3, 10),
            data_fim=date(2026, 3, 12),
            status=Evento.STATUS_RASCUNHO,
        )
        self.oficio = Oficio.objects.create(
            evento=self.evento,
            protocolo='123456789',
            data_criacao=date(2026, 3, 1),
            status=Oficio.STATUS_RASCUNHO,
        )

    def test_oficio_pode_ter_uma_justificativa(self):
        justificativa = Justificativa.objects.create(oficio=self.oficio, texto='Texto inicial')

        self.assertEqual(justificativa.oficio_id, self.oficio.id)
        self.assertEqual(Justificativa.objects.filter(oficio=self.oficio).count(), 1)

    def test_nao_permite_duas_justificativas_para_mesmo_oficio(self):
        Justificativa.objects.create(oficio=self.oficio, texto='Primeira')

        with self.assertRaises(IntegrityError):
            Justificativa.objects.create(oficio=self.oficio, texto='Segunda')

    def test_tela_do_oficio_edita_justificativa_existente_sem_duplicar(self):
        modelo = ModeloJustificativa.objects.create(nome='Padrao', texto='Modelo', padrao=True, ativo=True)
        Justificativa.objects.create(oficio=self.oficio, modelo=modelo, texto='Texto antigo')

        response = self.client.post(
            reverse('eventos:oficio-justificativa', kwargs={'pk': self.oficio.pk}),
            data={
                'modelo_justificativa': str(modelo.pk),
                'justificativa_texto': 'Texto atualizado',
                'next': reverse('eventos:oficio-step4', kwargs={'pk': self.oficio.pk}),
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Justificativa.objects.filter(oficio=self.oficio).count(), 1)
        self.assertEqual(Justificativa.objects.get(oficio=self.oficio).texto, 'Texto atualizado')

    def test_renderizacao_da_justificativa_usa_model_novo(self):
        Justificativa.objects.create(oficio=self.oficio, texto='Texto vindo do model Justificativa')

        context = build_justificativa_document_context(self.oficio)

        self.assertEqual(context['conteudo']['justificativa_texto'], 'Texto vindo do model Justificativa')

    def test_renderizacao_nao_usa_fallback_para_campo_legado_oficio(self):
        context = build_justificativa_document_context(self.oficio)

        self.assertEqual(context['conteudo']['justificativa_texto'], '')

    def test_renderizacao_nao_usa_documento_avulso_como_fallback(self):
        DocumentoAvulso.objects.create(
            titulo='Justificativa avulsa antiga',
            tipo_documento=DocumentoAvulso.TIPO_JUSTIFICATIVA,
            conteudo_texto='Texto avulso legado',
            oficio=self.oficio,
            criado_por=self.user,
        )

        context = build_justificativa_document_context(self.oficio)

        self.assertEqual(context['conteudo']['justificativa_texto'], '')
