from models import schema
from printers import printer
from utils import print_util, string_util, java_type_util
from sqlglot.expressions import DataType


class HdportalPGPrinter(printer.Printer):

    def __init__(self):
        pass

    def name(self) -> str:
        return "hdportal-pg实现"

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
                    f'SELECT rb_create_unique_key(\'{table.name}\', \'{idx.name}\', \'{', '.join(idx.columns)}\', \'\');')
            else:
                print(
                    f'SELECT rb_create_index(\'{table.name}\', \'{idx.name}\', \'{', '.join(idx.columns)}\', null, null, null);')
        pass

    def print_function_call(self, command: schema.Command):
        pass


class HdportalOraclePrinter(printer.Printer):

    def __init__(self):
        pass

    def name(self) -> str:
        return "hdportal-oracle实现"

    def print_create_table(self, table: schema.Table):
        print(f"call rb_create_table('{table.name}', '")

        column_holder = print_util.ColumnHolder()
        for column in table.columns:
            row_parts: list[str] = [column.name]
            match column.data_type:
                case DataType.Type.VARCHAR.name:
                    row_parts.append(f'VARCHAR({column.length} CHAR)')
                case DataType.Type.BIT.name | DataType.Type.BOOLEAN.name:
                    row_parts.append('BOOLEAN')
                case DataType.Type.DECIMAL.name:
                    row_parts.append(f'DECIMAL({print_util.format_decimal(column.length)})')
                case DataType.Type.DATETIME.name:
                    row_parts.append('TIMESTAMP(0)')
                case DataType.Type.TEXT.name:
                    row_parts.append('CLOB')
                case DataType.Type.BIGINT.name:
                    row_parts.append('NUMBER(19)')
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
            column_format_sql += f'  PRIMARY KEY ({', '.join(table.pks[0].columns)})\', NULL);'
            pass
        else:
            column_format_sql += ', NULL);'
        print(column_format_sql)

        # 索引
        for idx in table.idxes:
            idx_name = idx.name
            if len(idx_name) > 30:
                act_name = []
                for i, element in enumerate(idx_name.split('_')):
                    if i == 0:
                        act_name.append(element)
                    else:
                        act_name.append(element[0])
                idx_name = '_'.join(act_name)
            if idx.unique:
                print(
                    f'call rb_create_unique_key(\'{table.name}\', \'{idx_name}\', \'{', '.join(idx.columns)}\', null);')
            else:
                print(
                    f'call rb_create_index(\'{table.name}\', \'{idx_name}\', \'{', '.join(idx.columns)}\', null);')
        pass

    def print_function_call(self, command: schema.Command):
        pass


class HdportalJavaPrinter(printer.Printer):

    def __init__(self):
        pass

    def name(self) -> str:
        return "hdportal-java实现"

    def print_create_table(self, table: schema.Table):
        class_name = string_util.to_camel_case(table.name.removeprefix('hp_'))

        print(f'@SchemaMeta')
        print(f'@MapToEntity({class_name}Bo.class)')
        if len(table.pks) > 0:
            pk = table.pks[0]
            if len(pk.columns) > 1:
                value = ', '.join(map(lambda x: f'{class_name}Schema.{x.upper()}', pk.columns))
                print(f'@PrimaryKey({{ {value} }})')
                pass
            else:
                print(f'@PrimaryKey({class_name}Schema.{pk.columns[0].upper()})')
            pass
        print(f'public class {class_name}Schema {{')
        print(f'  public static final String TABLE_NAME = "{table.name}";')
        print('  @NotColumnName')
        print('  public static final String TABLE_ALIAS = Consts.UNDERLINE + TABLE_NAME;')
        print()
        for column in table.columns:
            print(f'  public static final String {column.name.upper()} = "{column.name}";')
        print('}')
        print()
        for column in table.columns:
            if len(column.comment) > 0:
                print(f'  /** {column.comment} */')
            java_type = java_type_util.db_type_to_java_type(column.data_type)
            variable = string_util.to_program_variable(column.name)
            print(f'  private {java_type} {variable};')
        print()
    pass

    def print_function_call(self, command: schema.Command):
        pass
