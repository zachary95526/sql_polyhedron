from sqlglot.expressions import DataType


def is_number(column_type):
    return (column_type == DataType.Type.BIGINT.name or column_type == DataType.Type.INT.name
            or column_type == DataType.Type.DECIMAL.name)


def is_bool(column_type):
    return column_type == DataType.Type.BOOLEAN.name or column_type == DataType.Type.BIT.name


def is_datetime(column_type):
    return column_type == DataType.Type.DATETIME.name
