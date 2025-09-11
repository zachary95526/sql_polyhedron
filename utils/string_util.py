def to_camel_case(snake_str):
    """
    下划线转驼峰

    :param snake_str: 下划线
    :return: 驼峰输出
    """
    components = snake_str.split('_')
    return ''.join(x.title() for x in components)


def to_program_variable(snake_str):
    """
    下划线转程序变量。首字母小写，其他下划线转驼峰

    :param snake_str: 下划线
    :return: 驼峰输出
    """
    components = snake_str.split('_')
    result = components[0].lower()
    result += ''.join(x.title() for x in components[1:])
    return result
