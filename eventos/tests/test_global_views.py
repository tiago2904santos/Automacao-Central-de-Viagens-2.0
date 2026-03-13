from datetime import date, datetime, time

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from cadastros.models import Cargo, Estado, Cidade, UnidadeLotacao, Viajante
from eventos.models import (
    Evento,
    EventoFundamentacao,
    EventoTermoParticipante,
    ModeloJustificativa,
    Oficio,
    OficioTrecho,
    RoteiroEvento,
    RoteiroEventoDestino,
    RoteiroEventoTrecho,
)

User = get_user_model()


class GlobalViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='global', password='global123')
        self.client.login(username='global', password='global123')

        self.estado = Estado.objects.create(codigo_ibge='41', nome='Parana', sigla='PR', ativo=True)
        self.cidade_origem = Cidade.objects.create(codigo_ibge='4106902', nome='Curitiba', estado=self.estado, ativo=True)
        self.cidade_destino = Cidade.objects.create(codigo_ibge='4113700', nome='Londrina', estado=self.estado, ativo=True)
        self.cargo = Cargo.objects.create(nome='ANALISTA GLOBAL')
        self.unidade = UnidadeLotacao.objects.create(nome='UNIDADE GLOBAL')
        self.viajante = Viajante.objects.create(
            nome='VIAJANTE GLOBAL',
            status=Viajante.STATUS_FINALIZADO,
            cargo=self.cargo,
            cpf='52998224725',
            telefone='41999998888',
            unidade_lotacao=self.unidade,
            rg='123456789',
        )

        self.evento_pt = Evento.objects.create(
            titulo='Evento PT',
            data_inicio=date(2026, 3, 10),
            data_fim=date(2026, 3, 12),
            status=Evento.STATUS_EM_ANDAMENTO,
            cidade_base=self.cidade_origem,
        )
        self.evento_os = Evento.objects.create(
            titulo='Evento OS',
            data_inicio=date(2026, 4, 10),
            data_fim=date(2026, 4, 12),
            status=Evento.STATUS_EM_ANDAMENTO,
            cidade_base=self.cidade_origem,
        )
        self.fundamentacao_pt = EventoFundamentacao.objects.create(
            evento=self.evento_pt,
            tipo_documento=EventoFundamentacao.TIPO_PT,
            texto_fundamentacao='Plano global',
            coordenador_administrativo=self.viajante,
            horario_atendimento='08:00 as 17:00',
        )
        self.fundamentacao_os = EventoFundamentacao.objects.create(
            evento=self.evento_os,
            tipo_documento=EventoFundamentacao.TIPO_OS,
            texto_fundamentacao='Ordem global',
        )

        self.oficio_pt = Oficio.objects.create(
            evento=self.evento_pt,
            protocolo='123456789',
            data_criacao=date(2026, 3, 1),
            tipo_destino=Oficio.TIPO_DESTINO_INTERIOR,
            status=Oficio.STATUS_RASCUNHO,
        )
        self.oficio_pt.viajantes.add(self.viajante)
        OficioTrecho.objects.create(
            oficio=self.oficio_pt,
            ordem=0,
            origem_estado=self.estado,
            origem_cidade=self.cidade_origem,
            destino_estado=self.estado,
            destino_cidade=self.cidade_destino,
            saida_data=date(2026, 3, 10),
            saida_hora=time(8, 0),
            chegada_data=date(2026, 3, 10),
            chegada_hora=time(12, 0),
        )

        self.oficio_os = Oficio.objects.create(
            evento=self.evento_os,
            protocolo='987654321',
            data_criacao=date(2026, 4, 1),
            tipo_destino=Oficio.TIPO_DESTINO_CAPITAL,
            status=Oficio.STATUS_RASCUNHO,
        )
        self.oficio_os.viajantes.add(self.viajante)
        OficioTrecho.objects.create(
            oficio=self.oficio_os,
            ordem=0,
            origem_estado=self.estado,
            origem_cidade=self.cidade_origem,
            destino_estado=self.estado,
            destino_cidade=self.cidade_destino,
            saida_data=date(2026, 4, 10),
            saida_hora=time(9, 0),
            chegada_data=date(2026, 4, 10),
            chegada_hora=time(13, 0),
        )

        self.roteiro = RoteiroEvento.objects.create(
            evento=self.evento_pt,
            origem_estado=self.estado,
            origem_cidade=self.cidade_origem,
            saida_dt=timezone.make_aware(datetime(2026, 3, 10, 8, 0)),
            chegada_dt=timezone.make_aware(datetime(2026, 3, 10, 12, 0)),
            status=RoteiroEvento.STATUS_FINALIZADO,
        )
        RoteiroEventoDestino.objects.create(
            roteiro=self.roteiro,
            estado=self.estado,
            cidade=self.cidade_destino,
            ordem=0,
        )
        RoteiroEventoTrecho.objects.create(
            roteiro=self.roteiro,
            ordem=0,
            tipo=RoteiroEventoTrecho.TIPO_IDA,
            origem_estado=self.estado,
            origem_cidade=self.cidade_origem,
            destino_estado=self.estado,
            destino_cidade=self.cidade_destino,
            saida_dt=timezone.make_aware(datetime(2026, 3, 10, 8, 0)),
            chegada_dt=timezone.make_aware(datetime(2026, 3, 10, 12, 0)),
        )

        self.roteiro_avulso = RoteiroEvento.objects.create(
            evento=None,
            origem_estado=self.estado,
            origem_cidade=self.cidade_origem,
            saida_dt=timezone.make_aware(datetime(2026, 5, 3, 6, 30)),
            chegada_dt=timezone.make_aware(datetime(2026, 5, 3, 10, 45)),
            status=RoteiroEvento.STATUS_FINALIZADO,
            tipo=RoteiroEvento.TIPO_AVULSO,
        )
        RoteiroEventoDestino.objects.create(
            roteiro=self.roteiro_avulso,
            estado=self.estado,
            cidade=self.cidade_destino,
            ordem=0,
        )
        RoteiroEventoTrecho.objects.create(
            roteiro=self.roteiro_avulso,
            ordem=0,
            tipo=RoteiroEventoTrecho.TIPO_IDA,
            origem_estado=self.estado,
            origem_cidade=self.cidade_origem,
            destino_estado=self.estado,
            destino_cidade=self.cidade_destino,
            saida_dt=timezone.make_aware(datetime(2026, 5, 3, 6, 30)),
            chegada_dt=timezone.make_aware(datetime(2026, 5, 3, 10, 45)),
        )

        EventoTermoParticipante.objects.create(
            evento=self.evento_pt,
            viajante=self.viajante,
            status=EventoTermoParticipante.STATUS_PENDENTE,
        )

    def test_lista_global_de_oficios_responde_200_e_filtra_por_protocolo(self):
        response = self.client.get(reverse('eventos:oficios-global'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lista de ofícios')
        self.assertContains(response, self.oficio_pt.numero_formatado)

        filtered = self.client.get(reverse('eventos:oficios-global'), {'protocolo': '12.345.678-9'})
        self.assertEqual(filtered.status_code, 200)
        self.assertContains(filtered, self.oficio_pt.numero_formatado)
        self.assertNotContains(filtered, self.oficio_os.protocolo_formatado)

    def test_lista_global_de_oficios_renderiza_cards_agrupados_por_documento(self):
        Oficio.objects.filter(pk=self.oficio_pt.pk).update(
            justificativa_texto='Justificativa global preenchida.',
            gerar_termo_preenchido=True,
        )

        response = self.client.get(reverse('eventos:oficios-global'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cadastro de ofício')
        self.assertNotContains(response, 'Ir para eventos')
        self.assertNotContains(response, 'Central documental')
        self.assertContains(response, 'oficio-process-card')
        self.assertContains(response, 'Ofício')
        self.assertContains(response, 'Justificativa')
        self.assertContains(response, 'Termo de autorização')
        self.assertContains(response, 'Abrir wizard')

    def test_lista_global_de_roteiros_renderiza_cards_para_evento_e_avulso(self):
        response = self.client.get(reverse('eventos:roteiros-global'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lista de roteiros')
        self.assertContains(response, 'Cadastro de roteiro')
        self.assertNotContains(response, 'Novo roteiro avulso')
        self.assertNotContains(response, '>Eventos<', html=True)
        self.assertContains(response, 'roteiro-vinculo-chip')
        self.assertContains(response, 'Avulso')
        self.assertContains(response, 'Vinculado a evento')
        self.assertContains(response, 'Usar no cadastro')
        self.assertContains(response, self.roteiro_avulso.origem_cidade.nome)

    def test_lista_global_de_planos_trabalho_renderiza_cards_no_padrao_novo(self):
        response = self.client.get(reverse('eventos:documentos-planos-trabalho'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lista de planos de trabalho')
        # Cadastro avulso de PT será reconstruído; por enquanto, apenas listagem.
        self.assertNotContains(response, 'Cadastro de plano de trabalho')
        self.assertNotContains(response, 'Voltar para documentos')
        self.assertNotContains(response, '>Oficios<', html=True)
        self.assertContains(response, 'oficio-process-card')
        self.assertContains(response, 'Plano de trabalho')
        self.assertContains(response, self.evento_pt.titulo)
        self.assertContains(response, self.viajante.nome)
        self.assertContains(response, 'Editar')
        self.assertContains(response, 'Visualizar')
        self.assertContains(response, self.oficio_pt.numero_formatado)
        self.assertNotContains(response, self.oficio_os.numero_formatado)

    def test_lista_global_de_justificativas_renderiza_cards_no_padrao_novo(self):
        modelo = ModeloJustificativa.objects.create(nome='Modelo urgente', texto='Texto base')
        self.oficio_pt.justificativa_modelo = modelo
        self.oficio_pt.justificativa_texto = 'Justificativa operacional registrada para cobertura global.'
        self.oficio_pt.save(update_fields=['justificativa_modelo', 'justificativa_texto'])

        response = self.client.get(reverse('eventos:documentos-justificativas'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lista de justificativas')
        self.assertContains(response, 'Cadastro de modelo')
        self.assertContains(response, 'oficio-process-card')
        self.assertContains(response, 'Justificativa - {}'.format(self.oficio_pt.numero_formatado))
        self.assertContains(response, modelo.nome)
        self.assertContains(response, 'Editar')
        self.assertContains(response, 'Visualizar')
        self.assertContains(response, 'PDF')
        self.assertContains(response, 'DOCX')
        self.assertContains(response, self.evento_pt.titulo)

    def test_lista_global_de_termos_renderiza_cards_enxutos(self):
        response = self.client.get(reverse('eventos:documentos-termos'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lista de termos')
        self.assertNotContains(response, 'Voltar para documentos')
        self.assertNotContains(response, 'Abrir termos')
        self.assertContains(response, 'term-process-card')
        self.assertContains(response, self.viajante.nome)
        self.assertContains(response, self.cargo.nome)
        self.assertContains(response, 'Completo')
        self.assertContains(response, self.evento_pt.titulo)
        self.assertContains(response, self.oficio_pt.numero_formatado)
        self.assertContains(response, 'Abrir / Editar')
        self.assertContains(response, 'PDF')
        self.assertContains(response, 'DOCX')

    def test_hubs_globais_principais_respondem_200(self):
        urls = [
            reverse('eventos:roteiros-global'),
            reverse('eventos:documentos-hub'),
            reverse('eventos:documentos-planos-trabalho'),
            reverse('eventos:documentos-ordens-servico'),
            reverse('eventos:documentos-justificativas'),
            reverse('eventos:documentos-termos'),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, url)

    def test_hubs_documentais_renderizam_contexto_real(self):
        response_pt = self.client.get(reverse('eventos:documentos-planos-trabalho'))
        self.assertContains(response_pt, 'Lista de planos de trabalho')
        self.assertContains(response_pt, self.evento_pt.titulo)
        self.assertContains(response_pt, self.oficio_pt.numero_formatado)

        response_os = self.client.get(reverse('eventos:documentos-ordens-servico'))
        self.assertContains(response_os, 'Lista de ordens')
        self.assertContains(response_os, self.evento_os.titulo)
        self.assertContains(response_os, self.oficio_os.numero_formatado)

        response_termos = self.client.get(reverse('eventos:documentos-termos'))
        self.assertContains(response_termos, self.viajante.nome)
        self.assertContains(response_termos, self.evento_pt.titulo)

    def test_simulacao_global_calcula_valor(self):
        response = self.client.post(
            reverse('eventos:simulacao-diarias'),
            data={
                'period_count': '1',
                'quantidade_servidores': '2',
                'saida_data_0': '2026-03-10',
                'saida_hora_0': '08:00',
                'destino_cidade_0': 'Londrina',
                'destino_uf_0': 'PR',
                'chegada_final_data': '2026-03-11',
                'chegada_final_hora': '12:00',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Resultado')
        self.assertContains(response, 'Valor por servidor')
