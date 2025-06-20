# Обработка csv файла
# Что нужно сделать?
# Нужно написать скрипт для обработки CSV-файла, поддерживающий операции: 
# фильтрацию с операторами «больше», «меньше» и «равно»
# агрегацию с расчетом среднего (avg), минимального (min) и максимального (max) значения

# Собираем прототип, поэтому всё по простому. 
# Фильтрацию и агрегацию делаем по одной любой колонке. Делать фильтрации с составными условия, например с and или or, 
# а также по нескольким колонкам одновременно не нужно. Фильтрация поддерживает любые колонки, то есть с текстовыми и числовыми значениями,
# а агрегация только числовые. Гарантируется что входные файлы валидны, например если в колонке числа, то там все значения числа. 
# Чтобы сфокусироваться на функционале и не отвлекаться на рутинные задачи (обработка аргументов скрипта, чтение файла и форматированный вывод),
# можно использовать стандартную библиотеку argparse и csv, а для красивого отображения в консоли установить библиотеку tabulate.
# Пример файла csv:
# ```
# name,brand,price,rating
# iphone 15 pro,apple,999,4.9
# galaxy s23 ultra,samsung,1199,4.8
# redmi note 12,xiaomi,199,4.6
# poco x5 pro,xiaomi,299,4.4
# ``` 

import argparse
import csv
from tabulate import tabulate
import math


def parse_where(where_str):
    if '>' in where_str:
        col, val = where_str.split('>')
        return col.strip(), '>', val.strip()
    elif '<' in where_str:
        col, val = where_str.split('<')
        return col.strip(), '<', val.strip()
    elif '=' in where_str:
        col, val = where_str.split('=')
        return col.strip(), '=', val.strip()
    else:
        raise ValueError("Неверное условие фильтрации")

def filter_rows(rows, column, operator, value):
    try:
        
        try:
            value = float(value)
            is_numeric = True
        except ValueError:
            is_numeric = False

        filtered = []
        for row in rows:
            cell = row[column]
            if is_numeric:
                cell = float(cell)
            
            if operator == '>' and cell > value:
                filtered.append(row)
            elif operator == '<' and cell < value:
                filtered.append(row)
            elif operator == '=' and cell == value:
                filtered.append(row)

        return filtered

    except Exception as e:
        print("Ошибка при фильтрации:", e)
        return []

def aggregate_column(rows, column, operation):
    try:
        values = []
        for row in rows:
            val = float(row[column])
            if math.isnan(val):
                continue
            values.append(val)
        if not values:
            return []
        if operation == 'avg':
            result = sum(values) / len(values)
        elif operation == 'min':
            result = min(values)
        elif operation == 'max':
            result = max(values)
        else:
            raise ValueError("Недопустимая агрегация")
        return [[operation], [round(result, 2)]]
    except Exception as e:
        print("Ошибка агрегации:", e)
        return []

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True)
    parser.add_argument('--where')
    parser.add_argument('--aggregate')

    args = parser.parse_args()
    
    with open(args.file, encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    
    if args.where:
        col, op, val = parse_where(args.where)
        rows = filter_rows(rows, col, op, val)

    if args.aggregate:
        agg_col, agg_op = args.aggregate.split('=')
        result = aggregate_column(rows, agg_col.strip(), agg_op.strip())
        print(tabulate(result, headers='firstrow', tablefmt='grid'))
    else:
        print(tabulate(rows, headers="keys", tablefmt="grid"))

if __name__ == "__main__":
    main()

      
      


    
