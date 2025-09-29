from models import schema
from parsers import parser
from printers.printer import Printer
from printers.hdportal import hdportal_printer

input: str = """
             create table if not exists hp_sync_privhp_request
             (
                 uuid            varchar(38) not null comment '主键',
                 app_id          varchar(38) not null comment 'hdportal应用id',
                 request_id      bigint      not null comment '服务端接收到请求时生成的雪花id',
                 request_payload text        not null comment '请求报文',
                 trace_id        varchar(50) not null comment 'trace_id',
                 created         datetime comment '创建时间',
                 creator_id      varchar(38) comment '创建人标识',
                 creator_name    varchar(128) comment '创建人名称',
                 primary key (uuid),
                 unique key uk_hp_sync_privhp_request_1 (request_id)
             ) engine = innodb
               default COLLATE utf8_bin comment '待同步私有化hdportal请求表';

             create table if not exists hp_tenant_sync_privhp_progress
             (
                 uuid               varchar(38) not null comment '主键',
                 tenant             varchar(16) not null comment 'uni租户id',
                 app_id             varchar(38) not null comment 'hdportal应用id',
                 current_request_id bigint      not null comment '当前处理的请求id',
                 sync_err_msg       varchar(255) comment '同步失败时的失败原因',
                 trace_id           varchar(50) not null comment 'trace_id',
                 created            datetime comment '创建时间',
                 creator_id         varchar(38) comment '创建人标识',
                 creator_name       varchar(128) comment '创建人名称',
                 primary key (uuid),
                 unique key uk_tenant_sync_privhp_progress_1 (tenant, app_id)
             ) engine = innodb
               default COLLATE utf8_bin comment '租户同步私有化hdportal进度';
             """


class CompositePrinter(Printer):
    printers: list[Printer] = [
        hdportal_printer.HdportalPGPrinter(),
        hdportal_printer.HdportalOraclePrinter(),
        # hdportal_printer.HdportalJavaPrinter(),
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
