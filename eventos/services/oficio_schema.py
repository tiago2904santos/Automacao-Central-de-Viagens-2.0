from functools import lru_cache

from django.db import connection
from django.db.utils import OperationalError, ProgrammingError


MIGRATION_0033_MESSAGE = 'Banco local desatualizado: aplique a migration 0033 do app eventos.'


def _table_columns(table_name):
    with connection.cursor() as cursor:
        return {
            column.name
            for column in connection.introspection.get_table_description(cursor, table_name)
        }


@lru_cache(maxsize=1)
def get_oficio_justificativa_schema_status():
    try:
        table_names = set(connection.introspection.table_names())
        if 'eventos_oficio' not in table_names:
            return {
                'available': False,
                'message': MIGRATION_0033_MESSAGE,
            }
        if 'eventos_justificativa' not in table_names:
            return {
                'available': False,
                'message': MIGRATION_0033_MESSAGE,
            }
        justificativa_columns = _table_columns('eventos_justificativa')
    except (OperationalError, ProgrammingError):
        return {
            'available': False,
            'message': MIGRATION_0033_MESSAGE,
        }

    required_columns = {'oficio_id', 'texto', 'modelo_id'}
    if not required_columns.issubset(justificativa_columns):
        return {
            'available': False,
            'message': MIGRATION_0033_MESSAGE,
        }

    return {
        'available': True,
        'message': '',
    }


def oficio_justificativa_schema_available():
    return get_oficio_justificativa_schema_status()['available']


def clear_oficio_justificativa_schema_cache():
    get_oficio_justificativa_schema_status.cache_clear()
