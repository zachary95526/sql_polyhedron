from sqlglot.expressions import DataType


def db_type_to_java_type(db_type):
    """
    数据库类型转java类型

    :param db_type: 数据库类型
    :return: java类型
    """
    if db_type == DataType.Type.VARCHAR.name or db_type == DataType.Type.TEXT.name:
        return 'String'
    elif db_type == DataType.Type.BIT.name or db_type == DataType.Type.BOOLEAN.name:
        return 'Boolean'
    elif db_type == DataType.Type.INT.name:
        return 'Integer'
    elif db_type == DataType.Type.BIGINT.name:
        return 'Long'
    elif db_type == DataType.Type.DATETIME.name:
        return 'Date'
    elif db_type == DataType.Type.DECIMAL.name:
        return 'BigDecimal'
    else:
        print(f'未映射的类型: {db_type}')
        return db_type
