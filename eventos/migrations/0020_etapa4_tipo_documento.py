# Generated manually for Etapa 4 tipo_documento (PT/OS)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0019_evento_fundamentacao_etapa4'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventofundamentacao',
            name='tipo_documento',
            field=models.CharField(
                blank=True,
                choices=[('PT', 'Plano de Trabalho'), ('OS', 'Ordem de Serviço')],
                default='',
                max_length=2,
                verbose_name='Tipo do documento',
            ),
        ),
    ]
