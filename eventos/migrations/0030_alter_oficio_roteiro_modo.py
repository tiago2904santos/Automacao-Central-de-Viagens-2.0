from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0029_oficio_gerar_termo_preenchido'),
    ]

    operations = [
        migrations.AlterField(
            model_name='oficio',
            name='roteiro_modo',
            field=models.CharField(
                blank=True,
                choices=[
                    ('EVENTO_EXISTENTE', 'Usar roteiro salvo'),
                    ('ROTEIRO_PROPRIO', 'Montar roteiro neste ofício'),
                ],
                default='ROTEIRO_PROPRIO',
                max_length=20,
                verbose_name='Modo do roteiro',
            ),
        ),
    ]
