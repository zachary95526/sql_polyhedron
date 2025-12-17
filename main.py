from models import schema
from parsers import parser
from printers.printer import Printer
from printers.hdportal import hdportal_printer

input: str = """
             create table if not exists hp_retail_app_artifact
             (
                 id                 varchar(38)  not null comment '主键',
                 app_id             varchar(38)  not null comment '应用id',
                 version_num        varchar(128) not null comment '版本号',
                 version_name       varchar(255) not null comment '版本名称',
                 state              varchar(38)  not null comment '状态。未发布-unpublish, 已发布-published',
                 h5_url             varchar(128) comment 'h5地址',
                 wgt_url            varchar(128) comment 'wgt地址',
                 publish_at         datetime comment '发布时间',
                 publisher_id       varchar(38) comment '发布人标识',
                 publisher_name     varchar(128) comment '发布认名称',
                 publish_desc       text comment '版本描述',

                 version            bigint       not null comment '版本号',
                 created            datetime comment '创建时间',
                 creator_id         varchar(38) comment '创建人标识',
                 creator_name       varchar(128) comment '创建人名称',
                 last_modified      datetime comment '最后修改时间',
                 last_modifier_id   varchar(38) comment '最后修改人标识',
                 last_modifier_name varchar(128) comment '最后修改人名称',
                 primary key (id),
                 unique key uk_retail_app_artifact_1 (app_id, version_num)
             ) engine = innodb
               default COLLATE utf8_bin comment '零售app应用制品';

             create table if not exists hp_retail_app_tenant_strategy
             (
                 id                 varchar(38) not null comment '主键',
                 tenant_id          varchar(38) not null comment '租户id',
                 app_id             varchar(38) not null comment '应用id',
                 artifact_id        varchar(38) not null comment '制品id',
                 state              varchar(38) not null comment '状态。未发布-unpublish, 已发布-published, 已禁用-disabled',
                 grayscale_strategy text comment '灰度策略',

                 version            bigint      not null comment '版本号',
                 created            datetime comment '创建时间',
                 creator_id         varchar(38) comment '创建人标识',
                 creator_name       varchar(128) comment '创建人名称',
                 last_modified      datetime comment '最后修改时间',
                 last_modifier_id   varchar(38) comment '最后修改人标识',
                 last_modifier_name varchar(128) comment '最后修改人名称',
                 primary key (id),
                 key idx_retail_app_tenant_strategy_1 (tenant_id, artifact_id)
             ) engine = innodb
               default COLLATE utf8_bin comment '零售app应用发布策略';

             create table if not exists hp_retail_app_tenant_eff_str
             (
                 id              varchar(38)  not null comment '主键',
                 tenant_id       varchar(38)  not null comment '租户id',
                 app_id          varchar(38)  not null comment '应用id',
                 artifact_id     varchar(38)  not null comment '制品id',
                 strategy_id     varchar(38)  not null comment '策略id',
                 priority        bigint       not null comment '优先级',
                 condition_type  varchar(20)  not null comment '条件类型。员工代码-employeeCode, 门店代码-storeCode, 设备id-deviceId',
                 condition_value varchar(255) not null comment '条件值',

                 created         datetime comment '创建时间',
                 creator_id      varchar(38) comment '创建人标识',
                 creator_name    varchar(128) comment '创建人名称',
                 primary key (id),
                 key idx_retail_app_tenant_eff_str_1 (tenant_id, strategy_id),
                 key idx_retail_app_tenant_eff_str_2 (tenant_id, condition_value, condition_type)
             ) engine = innodb
               default COLLATE utf8_bin comment '零售app应用生效中策略';

             """


class CompositePrinter(Printer):
    printers: list[Printer] = [
        hdportal_printer.HdportalPGPrinter(),
        hdportal_printer.HdportalOraclePrinter(),
        hdportal_printer.HdportalPolarDbOPrinter(),
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
