from django.contrib import admin
from .models import Evento, EventoFinalizacao, EventoFundamentacao, EventoTermoParticipante, ModeloJustificativa, ModeloMotivoViagem, Oficio


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo_demanda', 'status', 'data_inicio', 'data_fim', 'cidade_principal', 'updated_at')
    list_filter = ('status', 'tipo_demanda')
    search_fields = ('titulo',)
    ordering = ('-data_inicio', '-created_at')


@admin.register(EventoFundamentacao)
class EventoFundamentacaoAdmin(admin.ModelAdmin):
    list_display = ('evento', 'concluido', 'updated_at')
    list_filter = ('updated_at',)
    search_fields = ('texto_fundamentacao', 'observacoes_pt_os')
    raw_id_fields = ('evento',)


@admin.register(EventoTermoParticipante)
class EventoTermoParticipanteAdmin(admin.ModelAdmin):
    list_display = ('evento', 'viajante', 'status', 'updated_at')
    list_filter = ('status',)
    search_fields = ('viajante__nome',)
    raw_id_fields = ('evento', 'viajante')


@admin.register(EventoFinalizacao)
class EventoFinalizacaoAdmin(admin.ModelAdmin):
    list_display = ('evento', 'concluido', 'finalizado_em', 'finalizado_por', 'updated_at')
    list_filter = ('finalizado_em',)
    search_fields = ('observacoes_finais',)
    raw_id_fields = ('evento', 'finalizado_por')


@admin.register(Oficio)
class OficioAdmin(admin.ModelAdmin):
    list_display = ('id', 'numero_formatado', 'evento', 'status', 'protocolo', 'created_at')
    list_filter = ('status',)
    search_fields = ('protocolo',)
    raw_id_fields = ('evento',)
    ordering = ('-created_at',)


@admin.register(ModeloMotivoViagem)
class ModeloMotivoViagemAdmin(admin.ModelAdmin):
    list_display = ('id', 'codigo', 'nome', 'ordem', 'ativo', 'padrao')
    list_filter = ('ativo', 'padrao')
    search_fields = ('codigo', 'nome', 'texto')
    ordering = ('ordem', 'nome')


@admin.register(ModeloJustificativa)
class ModeloJustificativaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'padrao', 'ativo', 'updated_at')
    list_filter = ('padrao', 'ativo')
    search_fields = ('nome', 'texto')
    ordering = ('nome',)
