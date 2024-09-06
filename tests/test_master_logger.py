import unittest
import logging
import os
import tempfile
from unittest.mock import patch, MagicMock
from profi_log.master_logger import MasterLogger


class TestMasterLogger(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.temp_dir, "test.log")
        self.logger = None

    def tearDown(self):
        if self.logger:
            for handler in self.logger._logger.handlers[:]:
                handler.close()
                self.logger._logger.removeHandler(handler)
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
        os.rmdir(self.temp_dir)

    def test_init_with_name(self):
        self.logger = MasterLogger(self.log_file, name="test_logger")
        self.assertEqual(self.logger._logger.name, "test_logger")

    def test_init_without_name(self):
        self.logger = MasterLogger(self.log_file)
        self.assertEqual(self.logger._logger.name, "root")

    def test_log_levels(self):
        self.logger = MasterLogger(self.log_file, level="DEBUG")
        self.logger.debug("Отладочное сообщение")
        self.logger.info("Информационное сообщение")
        self.logger.warning("Предупреждение")
        self.logger.error("Сообщение об ошибке")
        self.logger.critical("Критическое сообщение")

        with open(self.log_file, "r", encoding="utf-8") as f:
            log_contents = f.read()

        self.assertIn("DEBUG", log_contents)
        self.assertIn("INFO", log_contents)
        self.assertIn("WARNING", log_contents)
        self.assertIn("ERROR", log_contents)
        self.assertIn("CRITICAL", log_contents)

    def test_temporary_log_level(self):
        self.logger = MasterLogger(self.log_file, level="INFO")

        self.logger.debug("Не должно логироваться")
        with self.logger.temporary_log_level("DEBUG"):
            self.logger.debug("Должно логироваться")
        self.logger.debug("Снова не должно логироваться")

        with open(self.log_file, "r", encoding="utf-8") as f:
            log_contents = f.read()

        self.assertEqual(log_contents.count("Должно логироваться"), 1)
        self.assertEqual(log_contents.count("Не должно логироваться"), 0)

    @patch('smtplib.SMTP')
    def test_setup_email_logging(self, mock_smtp):
        self.logger = MasterLogger(self.log_file)
        self.logger.setup_email_logging(
            smtp_server="smtp.example.com",
            port=587,
            sender="sender@example.com",
            password="password",
            recipients=["recipient@example.com"]
        )

        self.logger.critical("Тестовое критическое сообщение")

        mock_smtp.assert_called_once_with("smtp.example.com", 587)
        mock_smtp.return_value.__enter__.return_value.send_message.assert_called_once()

    def test_log_exception(self):
        self.logger = MasterLogger(self.log_file)

        try:
            raise ValueError("Тестовое исключение")
        except ValueError:
            self.logger.log_exception("Произошла ошибка")

        with open(self.log_file, "r", encoding="utf-8") as f:
            log_contents = f.read()

        self.assertIn("Произошла ошибка", log_contents)
        self.assertIn("ValueError: Тестовое исключение", log_contents)

    def test_log_function_call(self):
        self.logger = MasterLogger(self.log_file)

        @self.logger.log_function_call()
        def test_function(a, b):
            return a + b

        result = test_function(3, 4)

        with open(self.log_file, "r", encoding="utf-8") as f:
            log_contents = f.read()

        self.assertIn("Вызов функции test_function с аргументами: (3, 4)", log_contents)
        self.assertIn("Функция test_function завершила выполнение. Результат: 7", log_contents)
        self.assertEqual(result, 7)


if __name__ == '__main__':
    unittest.main()