from django.contrib import admin
from .models import (
    CoordenadorOperacional,
    DocumentoAvulso,
    EfetivoPlanoTrabalho,
    Evento,
    EventoFinalizacao,
    EventoFundamentacao,
    EventoTermoParticipante,
    ModeloJustificativa,
    ModeloMotivoViagem,
    Oficio,
    SolicitantePlanoTrabalho,
)


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo_demanda', 'status', 'data_inicio', 'data_fim', 'cidade_principal', 'updated_at')
    list_filter = ('status', 'tipo_demanda')
    search_fields = ('titulo',)
    ordering = ('-data_inicio', '-created_at')


@admin.register(SolicitantePlanoTrabalho)
class SolicitantePlanoTrabalhoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativo', 'ordem', 'is_padrao', 'updated_at')
    list_filter = ('ativo', 'is_padrao')
    search_fields = ('nome',)
    ordering = ('ordem', 'nome')


@admin.register(CoordenadorOperacional)
class CoordenadorOperacionalAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cargo', 'cidade', 'unidade', 'ativo', 'ordem', 'updated_at')
    list_filter = ('ativo',)
    search_fields = ('nome', 'cargo', 'cidade')
    ordering = ('ordem', 'nome')


@admin.register(EfetivoPlanoTrabalho)
class EfetivoPlanoTrabalhoAdmin(admin.ModelAdmin):
    list_display = ('evento', 'cargo', 'quantidade')
    list_filter = ('cargo',)
    raw_id_fields = ('evento',)
    ordering = ('evento', 'cargo__nome')


@admin.register(EventoFundamentacao)
class EventoFundamentacaoAdmin(admin.ModelAdmin):
    list_display = ('evento', 'tipo_documento', 'concluido', 'solicitante', 'updated_at')
    list_filter = ('tipo_documento', 'updated_at')
    search_fields = ('texto_fundamentacao', 'observacoes_pt_os', 'solicitante_outros')
    raw_id_fields = ('evento', 'solicitante', 'coordenador_operacional', 'coordenador_administrativo')


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


@admin.register(DocumentoAvulso)
class DocumentoAvulsoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'titulo',
        'tipo_documento',
        'classificacao',
        'evento',
        'oficio',
        'criado_por',
        'updated_at',
    )
    list_filter = ('tipo_documento', 'classificacao')
    search_fields = ('titulo',)
    raw_id_fields = ('evento', 'roteiro', 'plano_trabalho', 'oficio', 'criado_por')
    ordering = ('-updated_at',)


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
