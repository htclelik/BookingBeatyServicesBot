""" Модуль html_utils.py содержит вспомогательные функции для работы с HTML-разметкой и экранирования текста. """
import html
from html.parser import HTMLParser
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

def escape_html(text: str) -> str:
    """ Экранирует специальные HTML символы в строке.

    Аргументы:
        text: исходная строка.

    Возвращает:
        Строка с заменёнными спецсимволами (&, <, > и др.).
    """
    return html.escape(text)


class BalanceHTMLParser(HTMLParser):
    """ Класс для проверки сбалансированности HTML-тегов. """

    def __init__(self):
        super().__init__()
        self.stack = []
        self.valid = True

    def handle_starttag(self, tag, attrs):
        """ Обрабатывает открывающие теги. """
        self.stack.append(tag)

    def handle_endtag(self, tag):
        """ Обрабатывает закрывающие теги. """
        if not self.stack or self.stack[-1] != tag:
            self.valid = False
        else:
            self.stack.pop()


def check_html_balance(html_text: str) -> bool:
    """ Проверяет, что все HTML-теги корректно сбалансированы.

    Использует HTMLParser для последовательной обработки тегов.

    Аргументы:
        html_text: текст с HTML-разметкой.

    Возвращает:
        True, если все открытые теги закрыты корректно, иначе False.
    """
    parser = BalanceHTMLParser()
    try:
        parser.feed(html_text)
    except Exception as e:
        logger.error(f"Ошибка при разборе HTML: {e}")
        return False

    return parser.valid and not parser.stack
