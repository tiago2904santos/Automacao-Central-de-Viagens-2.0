import django.core.validators
import prestacao_contas.models
from django.db import migrations, models


TABLE_NAME = "prestacao_contas_prestacaoconta"


def ensure_columns(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(f"PRAGMA table_info({TABLE_NAME})")
        existing_columns = {row[1] for row in cursor.fetchall()}

    statements = []
    if "oficio_assinado" not in existing_columns:
        statements.append(f"ALTER TABLE {TABLE_NAME} ADD COLUMN oficio_assinado varchar(100) NULL")
    if "rt_assinado" not in existing_columns:
        statements.append(f"ALTER TABLE {TABLE_NAME} ADD COLUMN rt_assinado varchar(100) NULL")
    if "despacho_assinado" not in existing_columns:
        statements.append(f"ALTER TABLE {TABLE_NAME} ADD COLUMN despacho_assinado varchar(100) NULL")
    if "diario_bordo_assinado" not in existing_columns:
        statements.append(f"ALTER TABLE {TABLE_NAME} ADD COLUMN diario_bordo_assinado varchar(100) NULL")
    if "pdf_final" not in existing_columns:
        statements.append(f"ALTER TABLE {TABLE_NAME} ADD COLUMN pdf_final varchar(100) NULL")
    if "pdf_final_atualizado_em" not in existing_columns:
        statements.append(f"ALTER TABLE {TABLE_NAME} ADD COLUMN pdf_final_atualizado_em datetime NULL")
    if "pdf_final_desatualizado" not in existing_columns:
        statements.append(f"ALTER TABLE {TABLE_NAME} ADD COLUMN pdf_final_desatualizado bool NOT NULL DEFAULT 0")

    for statement in statements:
        schema_editor.execute(statement)


class Migration(migrations.Migration):
    dependencies = [
        ("prestacao_contas", "0007_prestacaoconta_comprovante_transferencia_and_more"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(ensure_columns, migrations.RunPython.noop),
            ],
            state_operations=[
                migrations.AddField(
                    model_name="prestacaoconta",
                    name="oficio_assinado",
                    field=models.FileField(
                        blank=True,
                        null=True,
                        upload_to=prestacao_contas.models._prestacao_assinado_upload_to,
                        validators=[django.core.validators.FileExtensionValidator(["pdf"])],
                        verbose_name="Oficio assinado",
                    ),
                ),
                migrations.AddField(
                    model_name="prestacaoconta",
                    name="rt_assinado",
                    field=models.FileField(
                        blank=True,
                        null=True,
                        upload_to=prestacao_contas.models._prestacao_assinado_upload_to,
                        validators=[django.core.validators.FileExtensionValidator(["pdf"])],
                        verbose_name="RT assinado",
                    ),
                ),
                migrations.AddField(
                    model_name="prestacaoconta",
                    name="despacho_assinado",
                    field=models.FileField(
                        blank=True,
                        null=True,
                        upload_to=prestacao_contas.models._prestacao_assinado_upload_to,
                        validators=[django.core.validators.FileExtensionValidator(["pdf"])],
                        verbose_name="Despacho assinado",
                    ),
                ),
                migrations.AddField(
                    model_name="prestacaoconta",
                    name="diario_bordo_assinado",
                    field=models.FileField(
                        blank=True,
                        null=True,
                        upload_to=prestacao_contas.models._prestacao_assinado_upload_to,
                        validators=[django.core.validators.FileExtensionValidator(["pdf"])],
                        verbose_name="Diario de bordo assinado",
                    ),
                ),
                migrations.AddField(
                    model_name="prestacaoconta",
                    name="pdf_final",
                    field=models.FileField(
                        blank=True,
                        null=True,
                        upload_to=prestacao_contas.models._prestacao_pdf_final_upload_to,
                        validators=[django.core.validators.FileExtensionValidator(["pdf"])],
                        verbose_name="PDF final",
                    ),
                ),
                migrations.AddField(
                    model_name="prestacaoconta",
                    name="pdf_final_atualizado_em",
                    field=models.DateTimeField(blank=True, null=True, verbose_name="PDF final atualizado em"),
                ),
                migrations.AddField(
                    model_name="prestacaoconta",
                    name="pdf_final_desatualizado",
                    field=models.BooleanField(default=False, verbose_name="PDF final desatualizado"),
                ),
            ],
        ),
    ]
