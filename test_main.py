import pytest
from main import parse_where, filter_rows, aggregate_column
import subprocess
import sys

python_executable = sys.executable

rows = [
    {"name": "iphone", "brand": "apple", "price": "999", "rating": "4.9"},
    {"name": "galaxy", "brand": "samsung", "price": "1199", "rating": "4.8"},
    {"name": "redmi", "brand": "xiaomi", "price": "199", "rating": "4.6"},
    {"name": "poco", "brand": "xiaomi", "price": "299", "rating": "4.4"},
]

# ---------- parse_where ----------
def test_parse_where_gt():
    assert parse_where("price>500") == ("price", ">", "500")

def test_parse_where_lt():
    assert parse_where("rating<4.9") == ("rating", "<", "4.9")

def test_parse_where_eq():
    assert parse_where("brand=apple") == ("brand", "=", "apple")

def test_parse_where_invalid():
    with pytest.raises(ValueError):
        parse_where("rating!4.5")

# ---------- filter_rows ----------
def test_filter_numeric_gt():
    result = filter_rows(rows, "price", ">", 500)
    assert len(result) == 2  # iphone и galaxy

def test_filter_numeric_lt():
    result = filter_rows(rows, "rating", "<", 4.7)
    assert len(result) == 2  # redmi и poco

def test_filter_text_eq():
    result = filter_rows(rows, "brand", "=", "xiaomi")
    assert len(result) == 2

def test_filter_empty_result():
    result = filter_rows(rows, "price", ">", 2000)
    assert result == []

def test_filter_invalid_column():
    # Проверка обработки ошибки при несуществующей колонке
    result = filter_rows(rows, "nonexistent", "=", "val")
    assert result == []

# ---------- aggregate_column ----------
def test_aggregate_avg():
    result = aggregate_column(rows, "price", "avg")
    expected_avg = round((999 + 1199 + 199 + 299) / 4, 2)
    assert result == [["avg"], [expected_avg]]

def test_aggregate_min():
    result = aggregate_column(rows, "rating", "min")
    assert result == [["min"], [4.4]]

def test_aggregate_max():
    result = aggregate_column(rows, "rating", "max")
    assert result == [["max"], [4.9]]

def test_aggregate_invalid_operation():
    result = aggregate_column(rows, "price", "sum")
    assert result == []

def test_aggregate_column_error_nan():
    bad_rows = [{"price": "NaN"}]
    result = aggregate_column(bad_rows, "price", "avg")
    assert result == []

def test_aggregate_empty_rows():
    result = aggregate_column([], "price", "avg")
    assert result == []

def test_aggregate_invalid_column():
    # Колонка не существует
    result = aggregate_column(rows, "nonexistent", "avg")
    assert result == []

# ---------- main.py через subprocess ----------
def test_main_invalid_aggregate(tmp_path):
    csv_content = "name,brand,price,rating\niphone,apple,999,4.9"
    file = tmp_path / "badagg.csv"
    file.write_text(csv_content)

    result = subprocess.run(
        [python_executable, "main.py", "--file", str(file), "--aggregate", "price=sum"],
        capture_output=True,
        text=True
    )
    assert "Ошибка агрегации" in result.stdout

def test_main_with_args(tmp_path):
    csv_content = "name,brand,price,rating\niphone,apple,999,4.9\ngalaxy,samsung,1199,4.8"
    file = tmp_path / "data.csv"
    file.write_text(csv_content)

    result = subprocess.run(
        [python_executable, "main.py", "--file", str(file), "--where", "price>500"],
        capture_output=True,
        text=True
    )
    # Должен содержать iphone или galaxy
    assert "iphone" in result.stdout or "galaxy" in result.stdout

def test_main_with_aggregate_only(tmp_path):
    csv_content = "name,brand,price,rating\niphone,apple,999,4.9\ngalaxy,samsung,1199,4.8"
    file = tmp_path / "data.csv"
    file.write_text(csv_content)

    result = subprocess.run(
        [python_executable, "main.py", "--file", str(file), "--aggregate", "price=avg"],
        capture_output=True,
        text=True
    )
    assert "avg" in result.stdout
    assert "+" in result.stdout  # проверяем что есть рамки таблицы


def test_main_without_filters(tmp_path):
    csv_content = "name,brand,price,rating\niphone,apple,999,4.9\ngalaxy,samsung,1199,4.8"
    file = tmp_path / "raw.csv"
    file.write_text(csv_content)

    result = subprocess.run(
        [python_executable, "main.py", "--file", str(file)],
        capture_output=True,
        text=True
    )
    assert "iphone" in result.stdout
    assert "galaxy" in result.stdout
