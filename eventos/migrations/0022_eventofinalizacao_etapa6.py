# Generated manually for Etapa 6 — Finalização

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('eventos', '0021_eventotermoparticipante_etapa5'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventoFinalizacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('observacoes_finais', models.TextField(blank=True, default='', verbose_name='Observações finais')),
                ('finalizado_em', models.DateTimeField(blank=True, null=True, verbose_name='Finalizado em')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('evento', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='finalizacao',
                    to='eventos.evento',
                    verbose_name='Evento',
                )),
                ('finalizado_por', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='eventos_finalizados',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Finalizado por',
                )),
            ],
            options={
                'verbose_name': 'Finalização do evento',
                'verbose_name_plural': 'Finalizações do evento',
            },
        ),
    ]
