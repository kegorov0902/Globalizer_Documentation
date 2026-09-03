Использование Globalizer как библиотеки (C++ API)
=================================================

Globalizer можно использовать не только как консольное приложение, но и встраивать напрямую в ваши C++ проекты в виде статической (``.lib``) или динамической (``.dll``) библиотеки.

Этот раздел описывает основные публичные классы, функции, типы данных, инструкции по сборке и подключению и правила работы с API.

Быстрый старт
-------------

1. Сборка библиотеки
--------------------

Выполните эти команды в корневой папке репозитория Globalizer.

**Для динамической библиотеки (DLL):**

.. code-block:: powershell

    cmake -B build_dll -DGLOBALIZER_BUILD_AS_LIBRARY_ONLY=ON -DBUILD_SHARED_LIBS=ON -DGLOBALIZER_USE_MPI=OFF -DGLOBALIZER_USE_MP=OFF -DGLOBALIZER_USE_CUDA=OFF
    cmake --build build_dll --config Release
    cmake --install build_dll --prefix <ПУТЬ_ДО_ВАШЕГО_ПРОЕКТА>/sdk_dll

**Для статической библиотеки (LIB):**

.. code-block:: powershell

    cmake -B build_lib -DGLOBALIZER_BUILD_AS_LIBRARY_ONLY=ON -DBUILD_SHARED_LIBS=OFF -DGLOBALIZER_USE_MPI=OFF -DGLOBALIZER_USE_MP=OFF -DGLOBALIZER_USE_CUDA=OFF
    cmake --build build_lib --config Release
    cmake --install build_lib --prefix <ПУТЬ_ДО_ВАШЕГО_ПРОЕКТА>/sdk_lib

*После выполнения в указанной папке появятся директории `include/`, `lib/` и (для DLL) `bin/`.*

2. Исходный код примера
-----------------------

Самый простой способ задать задачу оптимизации — использовать класс ``ProblemFromFunctionPointers``, который позволяет передавать целевую функцию и ограничения в виде лямбда-выражений или указателей на функции, без необходимости создавать наследника базового класса.

Данный код одинаков для обоих вариантов подключения.

.. code-block:: cpp

    #include "Globalizer.h"

    double StronginC3Functionals(const double* y, int fNumber)
    {
    double res = 0.0;
    double x1 = y[0], x2 = y[1];
    switch (fNumber)
    {
    case 0: // ограничение 1
        res = 0.01 * ((x1 - 2.2) * (x1 - 2.2) + (x2 - 1.2) * (x2 - 1.2) - 2.25);
        break;
    case 1: // ограничение 2
        res = 100.0 * (1.0 - ((x1 - 2.0) / 1.2) * ((x1 - 2.0) / 1.2) -
        (x2 / 2.0) * (x2 / 2.0));
        break;
    case 2: // ограничение 3
        res = 10.0 * (x2 - 1.5 - 1.5 * sin(6.283 * (x1 - 1.75)));
        break;
    case 3: // критерий
    {
        double t1 = pow(0.5 * x1 - 0.5, 4.0);
        double t2 = pow(x2 - 1.0, 4.0);
        res = 1.5 * x1 * x1 * exp(1.0 - x1 * x1 - 20.25 * (x1 - x2) * (x1 - x2));
        res = res + t1 * t2 * exp(2.0 - t1 - t2);
        res = -res;
    }
    break;
    }

    return res;
    }

    // ------------------------------------------------------------------------------------------------
    int main(int argc, char* argv[])
    {

    GlobalizerInitialization(argc, argv);

    parameters.Dimension = 2; // Размерность задачи
    IProblem* problem = nullptr;
    parameters.IsPlot = true; // Включаем рисование графика функции с точками испытаний (сохраняются в файл)

    parameters.IsSerializeToDashBoard = true;

    parameters.Dimension = 2;
    problem = new ProblemFromFunctionPointers(parameters.Dimension, // размерность задачи
        { 0.0, -1.0 }, // нижняя граница
        { 4.0, 3.0 }, // верхняя граница
        StronginC3Functionals, // задача
        4 // количество функций (3 ограничения + 1 критерий)
    );

    parameters.ConstraintsGridSize = 250;
    parameters.FillFeasibleRegion = true;
    parameters.CalcsType = Interpolation;

    problem->Initialize();

    // Решатель
    Solver solver(problem);

    // Решаем задачу
    if (solver.Solve() != SYSTEM_OK)
        throw 1;

    if (parameters.IsMPIInit())
        MPI_Finalize();

    return 0;
    }

    // - end of file ----------------------------------------------------------------------------------

3. Вариант А: Использование динамической библиотеки (DLL)
---------------------------------------------------------

**CMakeLists.txt**

.. code-block:: cmake

    cmake_minimum_required(VERSION 3.15)
    project(GlobalizerDllExample)
    set(CMAKE_CXX_STANDARD 17)

    # Путь к папке sdk_dll, полученной после cmake --install
    set(SDK_PATH "${CMAKE_CURRENT_SOURCE_DIR}/sdk_dll")

    find_package(Globalizer REQUIRED PATHS "${SDK_PATH}")

    add_executable(app_dll main.cpp)

    # Линкуем основную библиотеку и заглушку MPI (так как собирали с MPI=OFF)
    target_link_libraries(app_dll PRIVATE 
        Globalizer::Globalizer_l
        "${SDK_PATH}/lib/mpi_stub.lib"
    )

    # ВАЖНО: Копируем DLL в папку с исполняемым файлом, чтобы Windows нашла её при запуске
    add_custom_command(TARGET app_dll POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
            $<TARGET_FILE:Globalizer::Globalizer_l>
            $<TARGET_FILE_DIR:app_dll>
    )

**Объяснение:**

``find_package`` автоматически прописывает пути к заголовкам (``include/``).

``mpi_stub.lib`` подключается явно, так как при ``MPI=OFF`` Globalizer требует эту заглушку для линковки функций ``MPI_Init`` / ``MPI_Finalize``.

Блок ``add_custom_command`` критически важен для DLL. Он автоматически копирует ``Globalizer_l.dll`` из ``bin/`` в папку сборки рядом с ``.exe`` после каждой компиляции.

Вариант Б: Использование статической библиотеки (LIB)
--------------------------------------------------------

**CMakeLists.txt**

.. code-block:: cmake

    cmake_minimum_required(VERSION 3.15)
    project(GlobalizerLibExample)
    set(CMAKE_CXX_STANDARD 17)

    # Путь к папке sdk_lib, полученной после cmake --install
    set(SDK_PATH "${CMAKE_CURRENT_SOURCE_DIR}/sdk_lib")

    find_package(Globalizer REQUIRED PATHS "${SDK_PATH}")

    add_executable(app_lib main.cpp)

    # Линкуем статическую библиотеку и заглушку MPI
    target_link_libraries(app_lib PRIVATE 
        Globalizer::Globalizer_l
        "${SDK_PATH}/lib/mpi_stub.lib"
    )

**Объяснение:**

Структура подключения идентична, но используется папка ``sdk_lib``.

Команда копирования DLL отсутствует, так как статическая библиотека (``.lib``) не требует наличия отдельных файлов при запуске. Весь необходимый код Globalizer компилятор встраивает напрямую в итоговый исполняемый файл ``app_lib.exe``.

Справочник API
--------------

Глобальные функции
~~~~~~~~~~~~~~~~~~

.. cpp:function:: void GlobalizerInitialization(int argc, char** argv, bool isMPIInit = false, ...)

   Инициализирует внутреннее состояние библиотеки, обрабатывает аргументы командной строки и настраивает глобальный объект ``parameters``.

   :param argc: Количество аргументов командной строки (из ``main``).
   :param argv: Массив аргументов командной строки (из ``main``).
   :param isMPIInit: Флаг, указывающий, должен ли Globalizer самостоятельно вызывать ``MPI_Init``.
   :throws: Может генерировать исключения при некорректных аргументах командной строки.

.. cpp:function:: int MPI_Finalize()

   Завершает работу MPI. **Обязательно** должен вызываться в конце ``main``, после удаления всех объектов ``Solver`` и ``IProblem``.

Классы задач оптимизации
~~~~~~~~~~~~~~~~~~~~~~~~

.. cpp:class:: IProblem

   Базовый абстрактный интерфейс для всех задач оптимизации. Если вы хотите реализовать свою сложную логику вычислений, создайте класс, наследуемый от ``IProblem``, и переопределите его чисто виртуальные методы.

   **Коды возврата методов:**
   
   ==================  ==================================================================
   Значение            Описание
   ==================  ==================================================================
   ``IProblem::OK``    (0) Операция выполнена успешно.
   ``UNDEFINED``       (-1) Параметр (например, точный оптимум) не определен для задачи.
   ``ERROR``           (-2) Произошла ошибка при выполнении операции.
   ==================  ==================================================================

.. cpp:class:: ProblemFromFunctionPointers : public IProblem

   Готовая реализация задачи, принимающая функции в виде ``std::function``. Идеально подходит для быстрых прототипов и задач, заданных аналитически.

   .. cpp:function:: ProblemFromFunctionPointers(int dimension, const std::vector<double>& lowerBounds, const std::vector<double>& upperBounds, const std::vector<std::function<double(const double*)>>& functions, int totalFunctionsCount)
      
      Конструктор задачи.
      
      :param dimension: Размерность пространства поиска.
      :param lowerBounds: Вектор нижних границ для каждой переменной.
      :param upperBounds: Вектор верхних границ для каждой переменной.
      :param functions: Вектор лямбда-функций или указателей на функции. Первые элементы считаются ограничениями (должны быть <= 0), последний элемент — целевой функцией (критерием).
      :param totalFunctionsCount: Общее количество переданных функций.

Класс решателя (Solver)
~~~~~~~~~~~~~~~~~~~~~~~

.. cpp:class:: Solver

   Основной класс, управляющий процессом глобальной оптимизации.

   .. cpp:function:: explicit Solver(IProblem* problem)
      
      Конструктор. Принимает указатель на задачу. Объект задачи должен оставаться в памяти на протяжении всего времени жизни ``Solver``.

   .. cpp:function:: int Initialize()
      
      Подготавливает внутренние структуры данных, выделяет память и выполняет первую итерацию поиска.
      
      :returns: ``IProblem::OK`` при успехе, ``IProblem::ERROR`` при ошибке (например, некорректная размерность).

   .. cpp:function:: int DoIteration(bool& finished)
      
      Выполняет один шаг алгоритма оптимизации.
      
      :param finished: Ссылка на булеву переменную, в которую будет записано ``true``, если выполнен критерий остановки.
      :returns: ``IProblem::OK`` при успехе, ``IProblem::ERROR`` при сбое вычислений.

   .. cpp:function:: int Solve()
      
      Альтернатива циклу ``DoIteration``. Запускает процесс оптимизации и блокирует выполнение до достижения критерия остановки или ошибки.
      
      :returns: ``IProblem::OK`` при успешном завершении, ``IProblem::ERROR`` при сбое.

   .. cpp:function:: SolutionResult* GetSolutionResult() const
      
      Возвращает указатель на структуру с результатами оптимизации.
      
      :returns: Указатель на ``SolutionResult``. **Внимание:** Память, выделенная под этот объект, должна быть освобождена вызывающей стороной с помощью оператора ``delete``.

Структура результата
~~~~~~~~~~~~~~~~~~~~

.. cpp:struct:: SolutionResult

   Содержит итоговую информацию о процессе оптимизации.

   .. cpp:member:: Trial* BestTrial
      
      Указатель на структуру ``Trial``, содержащую координаты лучшей найденной точки (``y``), значения функций в этой точке (``FuncValues``) и её индекс.

   .. cpp:member:: int TrialCount
      
      Общее количество выполненных испытаний (вычислений функций).

   .. cpp:member:: int IterationCount
      
      Количество итераций алгоритма.

Глобальные параметры
~~~~~~~~~~~~~~~~~~~~

.. cpp:var:: Parameters parameters

   Глобальный объект, хранящий все настройки алгоритма. Изменять его поля необходимо **до** вызова ``GlobalizerInitialization`` или ``Solver::Initialize``.

   Основные поля:
   
   * ``int Dimension``: Размерность задачи.
   * ``double Epsilon``: Требуемая точность решения.
   * ``int MaxNumOfPoints``: Максимальное допустимое количество испытаний (лимит остановки).
   * ``bool IsPrintResultToConsole``: Выводить ли краткий отчет в консоль по завершении.

Обработка ошибок и исключения
-----------------------------

* **Коды возврата:** Большинство методов API возвращают ``int``. Всегда проверяйте, что возвращаемое значение равно ``0`` (``IProblem::OK``).
* **Исключения C++:** Внутренние ошибки (например, деление на ноль в пользовательской функции, ошибки выделения памяти или некорректные параметры) могут генерировать стандартные исключения ``std::runtime_error`` или ``std::logic_error``. Рекомендуется оборачивать вызовы ``Solver::Solve()`` или цикл ``DoIteration`` в блок ``try-catch``.
* **Управление памятью:** Объекты, созданные через ``new`` (например, ``ProblemFromFunctionPointers``), и результаты, полученные через ``GetSolutionResult()``, должны быть явно удалены через ``delete`` перед вызовом ``MPI_Finalize()``.
