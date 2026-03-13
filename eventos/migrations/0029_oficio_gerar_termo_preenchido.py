from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0028_oficio_retorno_distancia_km_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='oficio',
            name='gerar_termo_preenchido',
            field=models.BooleanField(default=False, verbose_name='Gerar termo de autorização preenchido'),
        ),
    ]
