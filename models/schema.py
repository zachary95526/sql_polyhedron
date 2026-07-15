from enum import Enum, auto
from typing import Union

import sqlglot


class Column:
    """
    参数：
        type：sqlglot.expressions.DataType
    """
    name: str
    data_type: sqlglot.expressions.DataType
    length: str
    notnull: bool
    default: Union[str, bool, int]
    comment: str

    def __init__(self, name, data_type, length, notnull=False, default=None, comment=None):
        self.name = name
        self.data_type = data_type
        self.length = length
        self.notnull = notnull
        self.default = default
        self.comment = comment


class PrimaryKey:
    name: str
    columns: list[str]

    def __init__(self, name, columns):
        self.name = name
        self.columns = columns


class Index:
    name: str
    columns: list[str]
    unique: bool

    def __init__(self, name, columns, unique=False):
        self.name = name
        self.columns = columns
        self.unique = unique


class Table:
    name: str
    columns: list[Column]
    pks: list[PrimaryKey]
    idxes: list[Index]
    comment: str

    def __init__(self, name, columns, pks, idxes, comment=None):
        self.name = name
        self.columns = columns
        self.pks = pks
        self.idxes = idxes
        self.comment = comment


class InsertValue:
    column: str
    value_type: sqlglot.expressions.DataType.Type
    value: object


class InsertSql:
    table: str
    values: list[InsertValue]
    ignore: bool

    def __init__(self, table, values: list[InsertValue], ignore=False):
        self.table = table
        self.values = values
        self.ignore = ignore


class CommandType(Enum):
    # 建表
    TABLE_CREATE = auto()
    # 插入语句
    INSERT_SQL = auto()
    # 调用函数
    FUNCTION_CALL = auto()


class Command:
    def __init__(self, type: CommandType, value: Union[Table | InsertSql]):
        self.type = type
        self.value = value
