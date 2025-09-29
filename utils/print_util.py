class ColumnHolder:
    rows: list[list[str]]

    def __init__(self):
        self.rows = []
        pass

    def add_row(self, parts: list[str]):
        self.rows.append(parts)

    def to_sql(self) -> str:
        idx_max_len: dict[int, int] = {}
        for row in self.rows:
            for idx in range(len(row)):
                exist_max_len = idx_max_len.get(idx, 0)
                if len(row[idx]) > exist_max_len:
                    idx_max_len[idx] = len(row[idx])
        for row in self.rows:
            for idx in range(len(row)):
                if idx > 1:
                    # 只有字段+类型需要格式化
                    continue
                if idx == 1 and len(row) == 2:
                    # 如果没有第三部分，也不需要对齐
                    continue
                row[idx] = row[idx].ljust(idx_max_len[idx])
        result = ''
        for idx in range(len(self.rows)):
            line: str
            if idx != len(self.rows) - 1:
                line = '  ' + ' '.join(self.rows[idx]) + ',\n'
            else:
                line = '  ' + ' '.join(self.rows[idx])  # 可能表没主键
            result += line
        return result


def format_decimal(input: str) -> str:
    arr = input.split(',')
    if len(arr) <= 1:
        return input
    for idx in range(1, len(arr)):
        arr[idx] = arr[idx].strip()
    return ', '.join(arr)
