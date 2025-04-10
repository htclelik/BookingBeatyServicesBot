""" Модуль data_access.py определяет абстрактный интерфейс для доступа к данным.
В будущем здесь будут реализованы классы для работы с Google Sheets, PostgreSQL и другими источниками. """

from abc import ABC, abstractmethod

class DataAccessInterface(ABC):
    """ Абстрактный класс для доступа к данным. """
    @abstractmethod
    def get_master_info(self, master_id: int) -> dict:
        """ Извлекает информацию о мастере по его идентификатору. """
        pass

    @abstractmethod
    def get_services(self) -> list:
        """
        Возвращает список доступных услуг.
        """
        pass