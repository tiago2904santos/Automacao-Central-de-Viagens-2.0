from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0026_ajuste_roteiro_avulso_autogen'),
    ]

    operations = [
        migrations.AddField(
            model_name='oficio',
            name='tipo_origem',
            field=models.CharField(
                verbose_name='Origem',
                max_length=20,
                choices=[('AVULSO', 'Avulso'), ('EVENTO', 'Vinculado a evento')],
                default='EVENTO',
            ),
        ),
    ]

