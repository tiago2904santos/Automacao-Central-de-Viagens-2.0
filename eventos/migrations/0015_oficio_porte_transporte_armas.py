from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0014_delete_oficiocounter_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='oficio',
            name='porte_transporte_armas',
            field=models.BooleanField(default=True, verbose_name='Porte/transporte de armas'),
        ),
    ]
