# Generated manually - campos PT em EventoFundamentacao que faltavam no banco

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0030_alter_oficio_roteiro_modo'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventofundamentacao',
            name='titulo_plano',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='Título do plano'),
        ),
        migrations.AddField(
            model_name='eventofundamentacao',
            name='local_execucao',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='Município / local'),
        ),
        migrations.AddField(
            model_name='eventofundamentacao',
            name='periodo_execucao',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='Período'),
        ),
        migrations.AddField(
            model_name='eventofundamentacao',
            name='tem_coordenador_municipal',
            field=models.BooleanField(default=False, verbose_name='Há coordenador municipal'),
        ),
        migrations.AddField(
            model_name='eventofundamentacao',
            name='coordenador_municipal_nome',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='Coordenador municipal'),
        ),
        migrations.AddField(
            model_name='eventofundamentacao',
            name='atividades_customizadas',
            field=models.TextField(
                blank=True,
                default='',
                help_text='Uma atividade por linha.',
                verbose_name='Atividades customizadas',
            ),
        ),
        migrations.AddField(
            model_name='eventofundamentacao',
            name='locais_texto',
            field=models.TextField(blank=True, default='', verbose_name='Locais'),
        ),
        migrations.AddField(
            model_name='eventofundamentacao',
            name='cronograma_texto',
            field=models.TextField(blank=True, default='', verbose_name='Cronograma'),
        ),
        migrations.AddField(
            model_name='eventofundamentacao',
            name='materiais_equipamentos_texto',
            field=models.TextField(blank=True, default='', verbose_name='Materiais e equipamentos'),
        ),
    ]
