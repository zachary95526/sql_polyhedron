import string


def format_decimal(length) -> string:
    arr = length.split(',')
    if len(arr) == 1:
        return length
    for idx in range(1, len(arr)):
        arr[idx] = ' ' + arr[idx]
    return ', '.join(arr)
