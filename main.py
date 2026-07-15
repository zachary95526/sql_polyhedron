from models import schema
from parsers import parser
from printers.printer import Printer
from printers.hdportal import hdportal_printer

input: str = """
INSERT IGNORE INTO hp_resource_type(type, name, data_structure) VALUES('vendor', '供应商', 'table');
             """

if __name__ == "__main__":
    parser = parser.DefaultParser(dialect="mysql")
    commands = parser.parse(input)
    print()
    print(f'解析到: {len(commands)} 条命令')

    printers: list[Printer] = [
        hdportal_printer.HdportalOraclePrinter(),
        hdportal_printer.HdportalPolarDbOPrinter(),
        hdportal_printer.HdportalPGPrinter(),
        hdportal_printer.HdportalJavaPrinter(),
    ]
    for printer in printers:
        print('-- ', "*" * 10, f' {printer.name()}: ', " 开始 ", "*" * 10)
        for command in commands:
            if command.type == schema.CommandType.TABLE_CREATE:
                printer.print_create_table(command.value)
            elif command.type == schema.CommandType.INSERT_SQL:
                printer.print_insert_sql(command.value)
            else:
                print(f'不支持的命令')
            print()
        print('-- ', "*" * 10, f' {printer.name()}: ', " 结束 ", "*" * 10, '\n')
