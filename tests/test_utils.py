""" Модуль тестов для утилит, проверяющих корректность HTML-разметки. """
import pytest

from app.utils.data_utils import get_master_by_id
from app.utils.html_utils import check_html_balance, escape_html

def test_valid_html():
    valid_text = "<b>Привет, пользователь!</b>"
    assert check_html_balance(valid_text) is True

def test_invalid_html():
    invalid_text = "<b>Привет, пользователь!"
    assert check_html_balance(invalid_text) is False

def test_escape_html():
    raw_text = "<script>alert('Hello');</script>"
    escaped = escape_html(raw_text)
    assert escaped == "&lt;script&gt;alert(&#x27;Hello&#x27;);&lt;/script&gt;"


def test_get_master_by_id():
    # Корректный вариант
    correct_id = "7153628119"
    print(get_master_by_id(correct_id))

    # Неверный вариант (если по ошибке передается список)
    wrong_id = [7153628119]
    print(get_master_by_id(wrong_id))


test_get_master_by_id()
