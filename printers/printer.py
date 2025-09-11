from abc import ABC, abstractmethod
from models import schema


class Printer(ABC):

    @abstractmethod
    def name(self) -> str:
        """
        名称，在打印结果时体现

        :return: 名称
        """
        pass

    @abstractmethod
    def print_create_table(self, table: schema.Table):
        """
        打印表结构

        :param table: 解析后的建表命令
        """
        pass

    @abstractmethod
    def print_function_call(self, command: schema.Command):
        """
        调用函数/存储过程

        :param command: 解析后的sql命令
        """
        pass
