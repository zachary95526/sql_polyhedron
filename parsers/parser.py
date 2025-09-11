from abc import ABC, abstractmethod
from typing import List

from models import schema
from sqlglot import parse, exp


class Parser(ABC):

    @abstractmethod
    def parse(self, sql) -> list[schema.Command]:
        """解析sql为表结构
        参数：
            sql（string）：sql语句
        返回：
            表结构列表
        """
        pass


class ExpressionHandler(ABC):

    @abstractmethod
    def support(self, expression) -> bool:
        pass

    @abstractmethod
    def handle(self, expression) -> schema.Command:
        pass


class DefaultParser(Parser):
    handlers: list[ExpressionHandler] = []

    def __init__(self, dialect=None):
        self.dialect = dialect

        self.handlers.append(CreateTableExpressionHandler(dialect=dialect))
        self.handlers.append(FunctionCallExpressionHandler())
        pass

    def parse(self, sql):
        expressions = parse(sql, self.dialect)
        result: List[schema.Command] = []
        for expression in expressions:
            for handler in self.handlers:
                if handler.support(expression):
                    command = handler.handle(expression)
                    if command:
                        result.append(command)
        return result


class CreateTableExpressionHandler(ExpressionHandler):

    def __init__(self, dialect=None):
        self.dialect = dialect
        pass

    def support(self, expression):
        return expression.find(exp.Create)

    def handle(self, expression):
        table = expression.find(exp.Table)

        table_name = table.name
        table_comment = ''
        for prop in expression.args.get('properties', []):
            if isinstance(prop, exp.SchemaCommentProperty):
                table_comment = prop.name
                break

        schema_columns: List[schema.Column] = []
        for column in expression.find_all(exp.ColumnDef):
            column_name = column.name
            column_type = None
            column_length = None
            kind = column.args["kind"]
            if kind:
                column_type = kind.this.name
                if kind.expressions:
                    len_arr = []
                    for e in kind.expressions:
                        len_arr.append(e.name)
                        column_length = ','.join(len_arr)
            schema_column: schema.Column = schema.Column(column_name, column_type, column_length)
            for constraint in column.args.get("constraints", []):
                if isinstance(constraint.kind, exp.NotNullColumnConstraint):
                    schema_column.notnull = True
                elif isinstance(constraint.kind, exp.DefaultColumnConstraint):
                    schema_column.default = constraint.kind.name
                elif isinstance(constraint.kind, exp.CommentColumnConstraint):
                    schema_column.comment = constraint.kind.name
            schema_columns.append(schema_column)

        pks: list[schema.PrimaryKey] = []
        idxes: list[schema.Index] = []
        for pk in expression.find_all(exp.PrimaryKey):
            idx_columns = [idx.name for idx in pk.args["expressions"]]
            pks.append(schema.PrimaryKey(None, idx_columns))
        for uk in expression.find_all(exp.UniqueColumnConstraint):
            idx_columns = [idx.name for idx in uk.this.expressions]
            idxes.append(schema.Index(uk.this.name, idx_columns, unique=True))
        for idx in expression.find_all(exp.IndexColumnConstraint):
            idx_columns = [idx.name for idx in idx.args["expressions"]]
            idxes.append(schema.Index(idx.name, idx_columns))

        schema_table = schema.Table(table_name, schema_columns, pks, idxes, comment=table_comment)
        return schema.Command(schema.CommandType.TABLE_CREATE, schema_table)


class FunctionCallExpressionHandler(ExpressionHandler):
    def support(self, expression):
        return False

    def handle(self, expression):
        return None
