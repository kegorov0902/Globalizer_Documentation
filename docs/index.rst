.. Globalizer documentation master file, created by
   sphinx-quickstart on Tue Oct 14 18:24:58 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Globalizer
========================

Библиотека Globalizer предназначена для численного решения задач многомерной
глобальной оптимизации с функциями вида «черный ящик», которые характеризуются
высокой вычислительной сложностью, большой размерностью, наличием частично
целочисленных параметров. Система позволяет проводить точную настройку параметров
моделей и методов из различных прикладных областей. Примерами таких задач являются
задачи настройки гиперпараметров методов искусственного интеллекта и машинного
обучения.

.. image:: source/html/Globalizer_logo.png
   :alt: A descriptive alt text for your image
   :width: 200px
   :align: center



.. toctree::
   :maxdepth: 2
   :caption: Основные функциональные возможности Globalizer:

   возможность работы с многоэкстремальными, многомерными функциями вида
«черный ящик»;
   возможность эффективной обработки ограничений различного типа, в частности,
невыпуклых ограничений;
   решение задач с частично вычислимыми (не всюду определенными) функциями;
   решение задач со смешанными (частично целочисленными) параметрами;
   возможность выбора начального приближения и точности вычислений;
   визуализация процесса решения задачи.

Исходный код находится 'здесь <https://github.com/OptimLLab/Globalizer>'_.

.. toctree::
   :maxdepth: 2
   :caption: Содержание:

   source/html/about_project
   source/html/mathematical
   source/html/installation
   source/html/start_of_work
