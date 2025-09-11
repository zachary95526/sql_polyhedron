from models import schema
from printers import printer
from utils import print_util
from sqlglot.expressions import DataType


class RumbaPGPrinter(printer.Printer):

    def __init__(self):
        pass

    def name(self) -> str:
        return "rumba-pg实现"

    def print_create_table(self, table: schema.Table):
        print(f"SELECT rb_create_table('{table.name}', '")

        column_holder = print_util.ColumnHolder()
        for column in table.columns:
            row_parts: list[str] = [column.name]
            match column.data_type:
                case DataType.Type.VARCHAR.name:
                    row_parts.append(f'VARCHAR({column.length})')
                case DataType.Type.BIT.name | DataType.Type.BOOLEAN.name:
                    row_parts.append('BOOLEAN')
                case DataType.Type.DECIMAL.name:
                    row_parts.append(f'DECIMAL({print_util.format_decimal(column.length)})')
                case DataType.Type.DATETIME.name:
                    row_parts.append('TIMESTAMP')
                case _:
                    if column.data_type:
                        row_parts.append(str(column.data_type))
                    else:
                        print('数据类型为空')
            third_part = []
            if column.notnull:
                third_part.append('NOT NULL')
            if column.default:
                if isinstance(column.default, str):
                    third_part.append(f'DEFAULT \'\'{column.default}\'\'')
                else:
                    third_part.append(f'DEFAULT {column.default}')
            if len(third_part) > 0:
                row_parts.append(' '.join(third_part))
            column_holder.add_row(row_parts)
        column_format_sql = column_holder.to_sql()

        if len(table.pks) > 0:
            column_format_sql += ',\n'
            column_format_sql += f'  PRIMARY KEY ({', '.join(table.pks[0].columns)})\', null);'
            pass
        else:
            column_format_sql += ', null);'
        print(column_format_sql)

        # 索引
        for idx in table.idxes:
            if idx.unique:
                print(
                    f'SELECT rb_create_unique_key(\'{table.name}\', \'{idx.name}\', \'{', '.join(idx.columns)}\');'', '');')
            else:
                print(
                    f'SELECT rb_create_index(\'{table.name}\', \'{idx.name}\', \'{', '.join(idx.columns)}\', null, null, null);')
        if len(table.comment) > 0:
            print(f'COMMENT ON TABLE {table.name} IS \'{table.comment}\';')
        for column in table.columns:
            if len(column.comment) > 0:
                print(f'COMMENT ON COLUMN {table.name}.{column.name} IS \'{column.comment}\';')
        pass

    def print_function_call(self, command: schema.Command):
        pass
