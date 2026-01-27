from models import schema
from parsers import parser
from printers.printer import Printer
from printers.hdportal import hdportal_printer

input: str = """
INSERT IGNORE INTO hp_menu (tenant, id, name, type, parent_menu_id, sort, url, icon, open_style, version, created, creator_id,
                            creator_name, last_modified, last_modifier_id, last_modifier_name)
VALUES ('*', 'zl-portal.securitySettingManage', '系统安全管理', 'func', 'zl-portal.loginConfig', 5.40, NULL, NULL, 'inside', 0,
  NULL, 'system', 'system', NULL, NULL, NULL);
             """


class CompositePrinter(Printer):
    printers: list[Printer] = [
        # hdportal_printer.HdportalPGPrinter(),
        # hdportal_printer.HdportalOraclePrinter(),
        # hdportal_printer.HdportalPolarDbOPrinter(),
        hdportal_printer.HdportalJavaPrinter(),
    ]

    def __init__(self):
        pass

    def name(self) -> str:
        return "聚合打印"

    def print_create_table(self, table):
        for p in self.printers:
            print('-- ', "*" * 10, f' {p.name()}: ', " 开始 ", "*" * 10)
            p.print_create_table(table)
            print('-- ', "*" * 10, f' {p.name()}: ', " 结束 ", "*" * 10, '\n')

    def print_function_call(self, command):
        for p in self.printers:
            p.print_function_call(command)


if __name__ == "__main__":
    parser = parser.DefaultParser(dialect="mysql")
    commands = parser.parse(input)
    print(f'解析到: {len(commands)} 条命令')
    printer = CompositePrinter()
    for command in commands:
        if command.type == schema.CommandType.TABLE_CREATE:
            printer.print_create_table(command.value)
        elif command.type == schema.CommandType.FUNCTION_CALL:
            printer.print_function_call(command)
        else:
            print(f'不支持的命令')
