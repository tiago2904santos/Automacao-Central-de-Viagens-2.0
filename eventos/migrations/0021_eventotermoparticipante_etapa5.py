# Generated manually for Etapa 5 — Termos (status por participante)

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cadastros', '0020_cidade_latitude_longitude'),
        ('eventos', '0020_etapa4_tipo_documento'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventoTermoParticipante',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(
                    choices=[('PENDENTE', 'Pendente'), ('DISPENSADO', 'Dispensado'), ('CONCLUIDO', 'Concluído')],
                    default='PENDENTE',
                    max_length=20,
                    verbose_name='Status do termo',
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('evento', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='termos_participantes',
                    to='eventos.evento',
                    verbose_name='Evento',
                )),
                ('viajante', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='eventos_termo_status',
                    to='cadastros.viajante',
                    verbose_name='Viajante',
                )),
            ],
            options={
                'verbose_name': 'Termo do participante (evento)',
                'verbose_name_plural': 'Termos dos participantes (evento)',
                'ordering': ['evento', 'viajante__nome'],
            },
        ),
        migrations.AddConstraint(
            model_name='eventotermoparticipante',
            constraint=models.UniqueConstraint(
                fields=('evento', 'viajante'),
                name='eventos_eventotermoparticipante_evento_viajante_unique',
            ),
        ),
    ]
