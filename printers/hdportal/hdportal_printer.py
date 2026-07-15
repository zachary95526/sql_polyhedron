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

    def print_insert_sql(self, command: schema.InsertSql):
        if command.table == 'hp_func':
            id = next((str(x.value) for x in command.values if x.column == 'id'), '')
            name = next((str(x.value) for x in command.values if x.column == 'name'), '')
            url = next((str(x.value) for x in command.values if x.column == 'url'), '')
            print(f'''INSERT INTO hp_func(app_id, id, simple_code, name, state, type, develop_technology, url, apply_to_os, version,
                    created, creator_id, creator_name, last_modified, last_modifier_id, last_modifier_name)
values ('zl-portal', '{id}', '{id}', '{name}', 'enabled', 'systemFunction', null,
        '{url}', null, 0, NULL, 'system', 'system', NULL, 'system', 'system') ON CONFLICT DO NOTHING;''')
            pass
        elif command.table == 'hp_org_type_func':
            org_type = next((str(x.value) for x in command.values if x.column == 'org_type'), '')
            func_id = next((str(x.value) for x in command.values if x.column == 'func_id'), '')
            print(f'''INSERT INTO hp_org_type_func(org_type, app_id, func_id)
values ('{org_type}', 'zl-portal', '{func_id}') ON CONFLICT DO NOTHING;''')
            pass
        elif command.table == 'hp_func_permission':
            func_id = next((str(x.value) for x in command.values if x.column == 'func_id'), '')
            id = next((str(x.value) for x in command.values if x.column == 'id'), '')
            name = next((str(x.value) for x in command.values if x.column == 'name'), '')
            remark = next((str(x.value) for x in command.values if x.column == 'remark'), '')
            print(f'''INSERT INTO hp_func_permission(app_id, func_id, id, name, type, remark, version, created, creator_id, creator_name,
                               last_modified, last_modifier_id, last_modifier_name)
values ('zl-portal', '{func_id}', '{id}', '{name}', 'func', '{remark}', 0, NULL, 'system', 'system', NULL, 'system',
        'system') ON CONFLICT DO NOTHING;''')
        elif command.table == 'hp_menu':
            id = next((str(x.value) for x in command.values if x.column == 'id'), '')
            name = next((str(x.value) for x in command.values if x.column == 'name'), '')
            type = next((str(x.value) for x in command.values if x.column == 'type'), '')
            parent_menu_id = next((str(x.value) for x in command.values if x.column == 'parent_menu_id'), '')
            sort = next((str(x.value) for x in command.values if x.column == 'sort'), '')
            print(f'''INSERT INTO hp_menu (tenant, id, name, type, parent_menu_id, sort, url, icon, open_style, version, created, creator_id,
                     creator_name, last_modified, last_modifier_id, last_modifier_name)
VALUES ('*', '{id}', '{name}', '{type}', '{parent_menu_id}', {sort}, NULL, NULL, NULL, 0, NULL,
        'system', 'system', NULL, NULL, NULL) ON CONFLICT DO NOTHING;''')
        elif command.table == 'hp_menu_func':
            menu_id = next((str(x.value) for x in command.values if x.column == 'menu_id'), '')
            func_id = next((str(x.value) for x in command.values if x.column == 'func_id'), '')
            print(f'''INSERT INTO hp_menu_func (tenant, app_id, menu_id, func_id, created, creator_id, creator_name)
VALUES ('*', 'zl-portal', '{menu_id}', '{func_id}', NULL, 'system', 'system') ON CONFLICT DO NOTHING;''')
        elif command.table == 'hp_builtin_command':
            id = next((str(x.value) for x in command.values if x.column == 'id'), '')
            biz_type = next((str(x.value) for x in command.values if x.column == 'biz_type'), '')
            args = next((str(x.value) for x in command.values if x.column == 'args'), '')
            print(f'''INSERT INTO hp_builtin_command (id, biz_type, args, state, version, created, creator_id, creator_name)
VALUES ('{id}', '{biz_type}', '{args}', 'ready', 0, null, 'upgrade', 'upgrade') ON CONFLICT DO NOTHING;''')
        elif command.table == 'hp_resource_type':
            type = next((str(x.value) for x in command.values if x.column == 'type'), '')
            name = next((str(x.value) for x in command.values if x.column == 'name'), '')
            data_structure = next((str(x.value) for x in command.values if x.column == 'data_structure'), '')
            print(
                f'''INSERT  INTO hp_resource_type(type, name, data_structure) VALUES('{type}', '{name}', '{data_structure}') ON CONFLICT DO NOTHING;''')
        pass


class HdportalOraclePrinter(printer.Printer):

    def __init__(self):
        pass

    def name(self) -> str:
        return "hdportal-oracle实现"

    def print_create_table(self, table: schema.Table):
        # 检查表名长度不能超过28，oracle会限制别名不能超过30，hdportal会加t_的前缀
        if len(table.name) > 29:
            raise ValueError(f'表{table.name}长度超过了28，请修改后再试')

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

    def print_insert_sql(self, command: schema.InsertSql):
        if command.table == 'hp_func':
            id = next((str(x.value) for x in command.values if x.column == 'id'), '')
            name = next((str(x.value) for x in command.values if x.column == 'name'), '')
            url = next((str(x.value) for x in command.values if x.column == 'url'), '')
            print(f'''INSERT /*+ IGNORE_ROW_ON_DUPKEY_INDEX(hp_func(app_id,id))*/ INTO  hp_func(app_id, id, simple_code, name, state, type, develop_technology, url, apply_to_os, version, created,
                                                                          creator_id, creator_name, last_modified, last_modifier_id, last_modifier_name)
values ('zl-portal', '{id}', '{id}', '{name}', 'enabled', 'systemFunction', null, '{url}', null,
        0, NULL, 'system', 'system', NULL, 'system', 'system');''')
            pass
        elif command.table == 'hp_org_type_func':
            org_type = next((str(x.value) for x in command.values if x.column == 'org_type'), '')
            func_id = next((str(x.value) for x in command.values if x.column == 'func_id'), '')
            print(f'''INSERT /*+ IGNORE_ROW_ON_DUPKEY_INDEX(hp_org_type_func(org_type,app_id,func_id))*/ INTO  hp_org_type_func(org_type, app_id, func_id)
values ('{org_type}', 'zl-portal', '{func_id}');''')
            pass
        elif command.table == 'hp_func_permission':
            func_id = next((str(x.value) for x in command.values if x.column == 'func_id'), '')
            id = next((str(x.value) for x in command.values if x.column == 'id'), '')
            name = next((str(x.value) for x in command.values if x.column == 'name'), '')
            remark = next((str(x.value) for x in command.values if x.column == 'remark'), '')
            print(f'''INSERT /*+ IGNORE_ROW_ON_DUPKEY_INDEX(hp_func_permission(app_id,id))*/ INTO  hp_func_permission(app_id, func_id, id, name, type, remark, version, created, creator_id, creator_name,last_modified, last_modifier_id, last_modifier_name)
values ('zl-portal', '{func_id}', '{id}', '{name}', 'func', '{remark}', 0, NULL, 'system', 'system', NULL, 'system','system');''')
        elif command.table == 'hp_menu':
            id = next((str(x.value) for x in command.values if x.column == 'id'), '')
            name = next((str(x.value) for x in command.values if x.column == 'name'), '')
            type = next((str(x.value) for x in command.values if x.column == 'type'), '')
            parent_menu_id = next((str(x.value) for x in command.values if x.column == 'parent_menu_id'), '')
            sort = next((str(x.value) for x in command.values if x.column == 'sort'), '')
            print(f'''INSERT /*+ IGNORE_ROW_ON_DUPKEY_INDEX(hp_menu(tenant,id))*/ INTO  hp_menu(tenant, id, name, type, parent_menu_id, sort, url, icon, open_style, version, created, creator_id,
                                                                          creator_name, last_modified, last_modifier_id, last_modifier_name)
VALUES ('*', '{id}', '{name}', '{type}', '{parent_menu_id}', {sort}, NULL, NULL, NULL, 0, NULL,
        'system', 'system', NULL, NULL, NULL);''')
        elif command.table == 'hp_menu_func':
            menu_id = next((str(x.value) for x in command.values if x.column == 'menu_id'), '')
            func_id = next((str(x.value) for x in command.values if x.column == 'func_id'), '')
            print(f'''INSERT /*+ IGNORE_ROW_ON_DUPKEY_INDEX(hp_menu_func(tenant, menu_id, app_id, func_id))*/ INTO  hp_menu_func(tenant, app_id, menu_id, func_id, created, creator_id, creator_name)
VALUES ('*', 'zl-portal', '{menu_id}', '{func_id}', NULL, 'system', 'system');''')
        elif command.table == 'hp_builtin_command':
            id = next((str(x.value) for x in command.values if x.column == 'id'), '')
            biz_type = next((str(x.value) for x in command.values if x.column == 'biz_type'), '')
            args = next((str(x.value) for x in command.values if x.column == 'args'), '')
            print(f'''INSERT /*+ IGNORE_ROW_ON_DUPKEY_INDEX(hp_builtin_command(id))*/ INTO hp_builtin_command (id, biz_type, args, state, version, created, creator_id, creator_name)
VALUES ('{id}', '{biz_type}', '{args}', 'ready', 0, null, 'upgrade', 'upgrade');''')
        elif command.table == 'hp_resource_type':
            type = next((str(x.value) for x in command.values if x.column == 'type'), '')
            name = next((str(x.value) for x in command.values if x.column == 'name'), '')
            data_structure = next((str(x.value) for x in command.values if x.column == 'data_structure'), '')
            print(
                f'''INSERT /*+ IGNORE_ROW_ON_DUPKEY_INDEX(hp_resource_type(type))*/ INTO hp_resource_type(type, name, data_structure) VALUES('{type}', '{name}', '{data_structure}');''')
        pass


class HdportalPolarDbOPrinter(printer.Printer):

    def __init__(self):
        pass

    def name(self) -> str:
        return "hdportal-polarDbOracle实现"

    def print_create_table(self, table: schema.Table):
        print(f"CALL rb_create_table('{table.name}', '")

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
                    f'CALL rb_create_unique_key(\'{table.name}\', \'{idx.name}\', \'{', '.join(idx.columns)}\', \'\');')
            else:
                print(
                    f'CALL rb_create_index(\'{table.name}\', \'{idx.name}\', \'{', '.join(idx.columns)}\', null, null, null);')
        pass

    def print_function_call(self, command: schema.Command):
        pass

    def print_insert_sql(self, command: schema.InsertSql):
        if command.table == 'hp_func':
            id = next((str(x.value) for x in command.values if x.column == 'id'), '')
            name = next((str(x.value) for x in command.values if x.column == 'name'), '')
            url = next((str(x.value) for x in command.values if x.column == 'url'), '')
            print(f'''INSERT INTO hp_func(app_id, id, simple_code, name, state, type, develop_technology, url, apply_to_os, version,
                    created, creator_id, creator_name, last_modified, last_modifier_id, last_modifier_name)
values ('zl-portal', '{id}', '{id}', '{name}', 'enabled', 'systemFunction', null,
        '{url}', null, 0, NULL, 'system', 'system', NULL, 'system', 'system') ON CONFLICT DO NOTHING;''')
            pass
        elif command.table == 'hp_org_type_func':
            org_type = next((str(x.value) for x in command.values if x.column == 'org_type'), '')
            func_id = next((str(x.value) for x in command.values if x.column == 'func_id'), '')
            print(f'''INSERT INTO hp_org_type_func(org_type, app_id, func_id)
values ('{org_type}', 'zl-portal', '{func_id}') ON CONFLICT DO NOTHING;''')
            pass
        elif command.table == 'hp_func_permission':
            func_id = next((str(x.value) for x in command.values if x.column == 'func_id'), '')
            id = next((str(x.value) for x in command.values if x.column == 'id'), '')
            name = next((str(x.value) for x in command.values if x.column == 'name'), '')
            remark = next((str(x.value) for x in command.values if x.column == 'remark'), '')
            print(f'''INSERT INTO hp_func_permission(app_id, func_id, id, name, type, remark, version, created, creator_id, creator_name,
                               last_modified, last_modifier_id, last_modifier_name)
values ('zl-portal', '{func_id}', '{id}', '{name}', 'func', '{remark}', 0, NULL, 'system', 'system', NULL, 'system',
        'system') ON CONFLICT DO NOTHING;''')
        elif command.table == 'hp_menu':
            id = next((str(x.value) for x in command.values if x.column == 'id'), '')
            name = next((str(x.value) for x in command.values if x.column == 'name'), '')
            type = next((str(x.value) for x in command.values if x.column == 'type'), '')
            parent_menu_id = next((str(x.value) for x in command.values if x.column == 'parent_menu_id'), '')
            sort = next((str(x.value) for x in command.values if x.column == 'sort'), '')
            print(f'''INSERT INTO hp_menu (tenant, id, name, type, parent_menu_id, sort, url, icon, open_style, version, created, creator_id,
                     creator_name, last_modified, last_modifier_id, last_modifier_name)
VALUES ('*', '{id}', '{name}', '{type}', '{parent_menu_id}', {sort}, NULL, NULL, NULL, 0, NULL,
        'system', 'system', NULL, NULL, NULL) ON CONFLICT DO NOTHING;''')
        elif command.table == 'hp_menu_func':
            menu_id = next((str(x.value) for x in command.values if x.column == 'menu_id'), '')
            func_id = next((str(x.value) for x in command.values if x.column == 'func_id'), '')
            print(f'''INSERT INTO hp_menu_func (tenant, app_id, menu_id, func_id, created, creator_id, creator_name)
VALUES ('*', 'zl-portal', '{menu_id}', '{func_id}', NULL, 'system', 'system') ON CONFLICT DO NOTHING;''')
        elif command.table == 'hp_builtin_command':
            id = next((str(x.value) for x in command.values if x.column == 'id'), '')
            biz_type = next((str(x.value) for x in command.values if x.column == 'biz_type'), '')
            args = next((str(x.value) for x in command.values if x.column == 'args'), '')
            print(f'''INSERT INTO hp_builtin_command (id, biz_type, args, state, version, created, creator_id, creator_name)
VALUES ('{id}', '{biz_type}', '{args}', 'ready', 0, null, 'upgrade', 'upgrade') ON CONFLICT DO NOTHING;''')
        elif command.table == 'hp_resource_type':
            type = next((str(x.value) for x in command.values if x.column == 'type'), '')
            name = next((str(x.value) for x in command.values if x.column == 'name'), '')
            data_structure = next((str(x.value) for x in command.values if x.column == 'data_structure'), '')
            print(
                f'''INSERT  INTO hp_resource_type(type, name, data_structure) VALUES('{type}', '{name}', '{data_structure}') ON CONFLICT DO NOTHING;''')
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
            field = column.name.upper()
            if column.name == 'created':
                field = 'CREATE_INFO_TIME'
            elif column.name == 'creator_id':
                field = 'CREATE_INFO_ID'
            elif column.name == 'creator_name':
                field = 'CREATE_INFO_NAME'
            elif column.name == 'last_modified':
                field = 'LAST_MODIFY_INFO_TIME'
            elif column.name == 'last_modifier_id':
                field = 'LAST_MODIFY_INFO_ID'
            elif column.name == 'last_modifier_name':
                field = 'LAST_MODIFY_INFO_NAME'
            print(f'  public static final String {field} = "{column.name}";')
        print('}')

        print()

        has_version: bool = False
        for column in table.columns:
            if column.name == 'version':
                has_version = True
                break
        print('@Getter')
        print('@Setter')
        if has_version:
            print(f'public class {class_name}Bo implements HasVersion {{')
        else:
            print(f'public class {class_name}Bo {{')
        for column in table.columns:
            if column.name == 'created':
                print(f'  /** 创建人信息 */')
                print(f'  private OperatorInfo createInfo;')
                continue
            elif column.name == 'creator_id':
                continue
            elif column.name == 'creator_name':
                continue
            elif column.name == 'last_modified':
                print(f'  /** 最后修改信息 */')
                print(f'  private OperatorInfo lastModifyInfo;')
                continue
            elif column.name == 'last_modifier_id':
                continue
            elif column.name == 'last_modifier_name':
                continue
            elif column.name == 'version':
                print(f'  /** 版本号 */')
                print(f'  private long version;')
                continue

            if len(column.comment) > 0:
                print(f'  /** {column.comment} */')
            java_type = java_type_util.db_type_to_java_type(column.data_type)
            variable = string_util.to_program_variable(column.name)
            print(f'  private {java_type} {variable};')
        print('}')

        print()
        print('@Repository')
        print(f'public class {class_name}Dao extends NewJdbcBaseDao<{class_name}Bo> {{')
        print(f'  private static final TEMapper<{class_name}Bo> MAPPER = TEMapperBuilder.of(')
        print(f'      {class_name}Bo.class, {class_name}Schema.class).build();')
        print('  private static final QueryProcessor QUERY_PROCESSOR = new QueryProcessorBuilder(')
        print(f'      {class_name}Bo.class, {class_name}Schema.class).build();')
        print()
        print('  @Override')
        print(f'  protected TEMapper<{class_name}Bo> getMapper() {{')
        print('    return MAPPER;')
        print('  }')
        print()
        print('  @Override')
        print('  protected QueryProcessor getQueryProcessor() {')
        print('    return QUERY_PROCESSOR;')
        print('  }')
        print()
        print('}')

        print()

        print('@Getter')
        print('@Setter')
        print(f'public class {class_name}Vo {{')
        for column in table.columns:
            if column.name == 'created':
                print(f'  @ApiModelProperty("创建人信息")')
                print(f'  private OperatorInfo createInfo;')
                continue
            elif column.name == 'creator_id':
                continue
            elif column.name == 'creator_name':
                continue
            elif column.name == 'last_modified':
                print(f'  @ApiModelProperty("最后更新人信息")')
                print(f'  private OperatorInfo lastModifyInfo;')
                continue
            elif column.name == 'last_modifier_id':
                continue
            elif column.name == 'last_modifier_name':
                continue
            elif column.name == 'version':
                print(f'  @ApiModelProperty(value = "版本号。只读")')
                print(f'  private long version;')
                continue

            if column.notnull:
                print(f'  @ApiModelProperty(value = "{column.comment}", required = true)')
            else:
                print(f'  @ApiModelProperty(value = "{column.comment}")')
            java_type = java_type_util.db_type_to_java_type(column.data_type)
            variable = string_util.to_program_variable(column.name)
            print(f'  private {java_type} {variable};')
        print('}')

    def print_function_call(self, command: schema.Command):
        pass

    def print_insert_sql(self, command: schema.InsertSql):
        pass
