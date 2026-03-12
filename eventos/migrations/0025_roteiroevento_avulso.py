from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0024_pt_solicitante_coordenador_efetivo_fundamentacao'),
    ]

    operations = [
        # Limpa trechos órfãos que referenciam roteiros inexistentes (necessário para SQLite ao alterar FKs).
        migrations.RunSQL(
            sql="""
                DELETE FROM eventos_roteiroeventotrecho
                WHERE roteiro_id IS NOT NULL
                  AND roteiro_id NOT IN (SELECT id FROM eventos_roteiroevento);
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.AlterField(
            model_name='roteiroevento',
            name='evento',
            field=models.ForeignKey(
                verbose_name='Evento',
                related_name='roteiros',
                to='eventos.evento',
                on_delete=models.deletion.CASCADE,
                null=True,
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name='roteiroevento',
            name='tipo',
            field=models.CharField(
                verbose_name='Tipo de roteiro',
                max_length=20,
                choices=[
                    ('EVENTO', 'Vinculado a evento'),
                    ('AVULSO', 'Avulso'),
                ],
                default='EVENTO',
            ),
        ),
    ]

