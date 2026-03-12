from django.shortcuts import render

from eventos.models import Evento, EventoTermoParticipante, Oficio
from eventos.views import _build_oficio_justificativa_info


def dashboard_view(request):
    oficios = list(Oficio.objects.prefetch_related('trechos').all())
    justificativas_pendentes = sum(
        1 for oficio in oficios if _build_oficio_justificativa_info(oficio)['status_key'] == 'pendente'
    )
    context = {
        'total_eventos': Evento.objects.count(),
        'total_oficios': len(oficios),
        'total_termos': EventoTermoParticipante.objects.count(),
        'total_pendencias': justificativas_pendentes + EventoTermoParticipante.objects.filter(
            status=EventoTermoParticipante.STATUS_PENDENTE
        ).count(),
    }
    return render(request, 'core/dashboard.html', context)
