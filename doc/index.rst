.. Profi Log documentation master file, created by
   sphinx-quickstart on Sat Sep  7 00:39:04 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Profi Log documentation
=======================

MasterLogger
============

.. autoclass:: profi_log.MasterLogger
   :members:
   :undoc-members:
   :show-inheritance:

Инициализация
-------------

.. automethod:: profi_log.MasterLogger.__init__

Методы настройки
----------------

setup_file_logging
^^^^^^^^^^^^^^^^^^

.. automethod:: profi_log.MasterLogger.setup_file_logging

setup_colored_console_logging
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: profi_log.MasterLogger.setup_colored_console_logging

setup_email_logging
^^^^^^^^^^^^^^^^^^^

.. automethod:: profi_log.MasterLogger.setup_email_logging

Вспомогательные методы
----------------------

temporary_log_level
^^^^^^^^^^^^^^^^^^^

.. automethod:: profi_log.MasterLogger.temporary_log_level

log_exception
^^^^^^^^^^^^^

.. automethod:: profi_log.MasterLogger.log_exception

log_function_call
^^^^^^^^^^^^^^^^^

.. automethod:: profi_log.MasterLogger.log_function_call

Методы логирования
------------------

debug
^^^^^

.. automethod:: profi_log.MasterLogger.debug

info
^^^^

.. automethod:: profi_log.MasterLogger.info

warning
^^^^^^^

.. automethod:: profi_log.MasterLogger.warning

error
^^^^^

.. automethod:: profi_log.MasterLogger.error

critical
^^^^^^^^

.. automethod:: profi_log.MasterLogger.critical

Примеры использования
---------------------

Базовое использование:

.. code-block:: python

   from profi_log import MasterLogger

   # Инициализация логгера
   logger = MasterLogger("app.log", level="DEBUG")

   # Настройка цветного консольного логирования
   logger.setup_colored_console_logging()

   # Использование логгера
   logger.info("Это информационное сообщение")
   logger.warning("Это предупреждение")
   logger.error("Это сообщение об ошибке")

Использование временного уровня логирования:

.. code-block:: python

   with logger.temporary_log_level("DEBUG"):
       logger.debug("Это отладочное сообщение")

Логирование исключений:

.. code-block:: python

   try:
       1 / 0
   except ZeroDivisionError:
       logger.log_exception("Произошла ошибка деления на ноль")

Использование декоратора для логирования вызовов функций:

.. code-block:: python

   @logger.log_function_call()
   def example_function(x, y):
       return x + y

   result = example_function(3, 4)


