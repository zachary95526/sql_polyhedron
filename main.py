from models import schema
from parsers import parser
from printers.printer import Printer
from printers.rumba import rumba_printer

input: str = """
create table if not exists apply_employee_ret
(
    tenant           varchar(16) not null comment 'uni 租户id',
    bill_id          varchar(38) not null comment '申请单号',
    id               varchar(38) not null comment '员工id',
    code             varchar(38) not null comment '员工代码',
    name             varchar(128) comment '员工名称',
    org_id           varchar(38) not null comment '组织id',
    org_code         varchar(38) not null comment '组织code',
    org_type         varchar(38) not null comment '组织类型',
    position_name    text comment '人事系统岗位',
    current_position text comment '当前申请人岗位',
    UNIQUE KEY uk_apply_employee_ret_1 (bill_id, id),
    KEY idx_apply_employee_ret_id (bill_id)
) engine = innodb
  default COLLATE utf8_bin comment = '申请员工退';
             """


class CompositePrinter(Printer):
    printers: list[Printer] = [
        # rumba
        rumba_printer.RumbaPGPrinter(),
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
