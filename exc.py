# Стандартные исключения Python: Когда какую ошибку ловить

## Иерархия исключений (важно!)

```
BaseException
├── SystemExit
├── KeyboardInterrupt
├── GeneratorExit
└── Exception  ← Обычно ловим это
    ├── StopIteration
    ├── ArithmeticError
    │   ├── ZeroDivisionError
    │   ├── OverflowError
    │   └── FloatingPointError
    ├── AssertionError
    ├── AttributeError
    ├── EOFError
    ├── ImportError
    │   └── ModuleNotFoundError
    ├── LookupError
    │   ├── IndexError
    │   └── KeyError
    ├── NameError
    │   └── UnboundLocalError
    ├── OSError
    │   ├── FileNotFoundError
    │   ├── PermissionError
    │   └── TimeoutError
    ├── RuntimeError
    │   ├── NotImplementedError
    │   └── RecursionError
    ├── TypeError
    ├── ValueError
    └── ... и другие
```

**Важно:** Ловите `Exception`, а не `BaseException` - иначе поймаете системные исключения (Ctrl+C, выход из программы)!

---

## 1. ValueError - неверное значение

**Когда возникает:** Правильный тип, но неправильное значение

```python
# Пример 1: Конвертация строки в число
try:
    age = int("abc")  # ❌ ValueError: invalid literal for int()
except ValueError:
    print("Это не число!")

# Пример 2: Распаковка неправильного количества элементов
try:
    a, b = [1, 2, 3]  # ❌ ValueError: too many values to unpack
except ValueError:
    print("Неправильное количество значений")

# Пример 3: Поиск в списке несуществующего элемента
try:
    lst = [1, 2, 3]
    index = lst.index(5)  # ❌ ValueError: 5 is not in list
except ValueError:
    print("Элемент не найден")

# Пример 4: Конвертация недопустимой строки
try:
    num = float("not a number")  # ❌ ValueError
except ValueError:
    print("Невозможно преобразовать в число")
```

**Типичные ситуации на лайвкодинге:**
```python
# Парсинг пользовательского ввода
def get_positive_number():
    try:
        num = int(input("Введите число: "))
        if num < 0:
            raise ValueError("Число должно быть положительным")
        return num
    except ValueError as e:
        print(f"Ошибка: {e}")
        return None
```

---

## 2. KeyError - ключ не найден в словаре

**Когда возникает:** Обращение к несуществующему ключу словаря

```python
# Пример 1: Отсутствующий ключ
try:
    d = {'a': 1, 'b': 2}
    value = d['c']  # ❌ KeyError: 'c'
except KeyError:
    print("Ключ не найден")

# Пример 2: Работа с JSON/API данными
try:
    user_data = {'name': 'Alice', 'email': 'alice@example.com'}
    phone = user_data['phone']  # ❌ KeyError: 'phone'
except KeyError:
    print("Поле 'phone' отсутствует")
    phone = None

# Пример 3: Удаление несуществующего ключа
try:
    d = {'a': 1}
    del d['b']  # ❌ KeyError: 'b'
except KeyError:
    print("Ключ уже удален или не существует")
```

**Альтернативы (лучше использовать!):**
```python
# ✅ Вместо try/except используйте .get()
d = {'a': 1, 'b': 2}
value = d.get('c', 'default')  # Не вызывает ошибку

# ✅ Проверка наличия ключа
if 'c' in d:
    value = d['c']

# ✅ defaultdict для счетчиков
from collections import defaultdict
counter = defaultdict(int)
counter['key'] += 1  # Не вызовет KeyError
```

---

## 3. IndexError - индекс вне диапазона

**Когда возникает:** Обращение по недопустимому индексу списка/кортежа

```python
# Пример 1: Индекс больше длины списка
try:
    lst = [1, 2, 3]
    item = lst[5]  # ❌ IndexError: list index out of range
except IndexError:
    print("Индекс вне диапазона")

# Пример 2: Пустой список
try:
    lst = []
    first = lst[0]  # ❌ IndexError
except IndexError:
    print("Список пустой")

# Пример 3: Отрицательный индекс (может быть валидным!)
try:
    lst = [1, 2, 3]
    item = lst[-10]  # ❌ IndexError
except IndexError:
    print("Индекс слишком отрицательный")
```

**Типичные ситуации:**
```python
# Обработка первого элемента
try:
    first_item = my_list[0]
except IndexError:
    print("Список пуст")
    first_item = None

# Или лучше:
first_item = my_list[0] if my_list else None

# Безопасный доступ к элементу
def safe_get(lst, index, default=None):
    try:
        return lst[index]
    except IndexError:
        return default

item = safe_get([1, 2, 3], 10, 'not found')
```

---

## 4. TypeError - неправильный тип

**Когда возникает:** Операция с неподдерживаемым типом данных

```python
# Пример 1: Конкатенация несовместимых типов
try:
    result = "Hello" + 5  # ❌ TypeError: can only concatenate str to str
except TypeError:
    print("Нельзя складывать строку и число")

# Пример 2: Неверное количество аргументов функции
try:
    def greet(name):
        return f"Hello, {name}"
    
    greet()  # ❌ TypeError: missing 1 required positional argument
except TypeError:
    print("Неправильные аргументы функции")

# Пример 3: Попытка индексации неиндексируемого объекта
try:
    num = 123
    digit = num[0]  # ❌ TypeError: 'int' object is not subscriptable
except TypeError:
    print("Этот тип не поддерживает индексацию")

# Пример 4: Вызов не-callable объекта
try:
    x = 5
    result = x()  # ❌ TypeError: 'int' object is not callable
except TypeError:
    print("Этот объект нельзя вызвать как функцию")

# Пример 5: Изменение неизменяемого объекта
try:
    t = (1, 2, 3)
    t[0] = 10  # ❌ TypeError: 'tuple' object does not support item assignment
except TypeError:
    print("Кортежи неизменяемы")

# Пример 6: Хеширование unhashable типа
try:
    d = {[1, 2]: 'value'}  # ❌ TypeError: unhashable type: 'list'
except TypeError:
    print("Списки нельзя использовать как ключи словаря")
```

---

## 5. AttributeError - атрибут не существует

**Когда возникает:** Обращение к несуществующему атрибуту объекта

```python
# Пример 1: Несуществующий метод/атрибут
try:
    s = "hello"
    s.append('!')  # ❌ AttributeError: 'str' object has no attribute 'append'
except AttributeError:
    print("У строки нет метода append")

# Пример 2: Обращение к None
try:
    result = None
    length = result.length  # ❌ AttributeError: 'NoneType' object has no attribute 'length'
except AttributeError:
    print("Объект None не имеет атрибутов")

# Пример 3: Ошибка в имени метода
try:
    lst = [1, 2, 3]
    lst.apend(4)  # ❌ AttributeError (опечатка в 'append')
except AttributeError:
    print("Метод не найден - проверьте правописание")

# Пример 4: Работа с опциональными объектами
class User:
    def __init__(self, name):
        self.name = name

try:
    user = None  # Пользователь не найден
    print(user.name)  # ❌ AttributeError
except AttributeError:
    print("Пользователь не инициализирован")
```

**Безопасные альтернативы:**
```python
# ✅ getattr с default значением
name = getattr(user, 'name', 'Anonymous')

# ✅ hasattr для проверки
if hasattr(user, 'name'):
    print(user.name)

# ✅ Optional chaining (Python 3.10+)
name = user.name if user else None
```

---

## 6. NameError - имя не определено

**Когда возникает:** Использование неопределенной переменной

```python
# Пример 1: Опечатка в имени переменной
try:
    my_variable = 10
    print(my_varaible)  # ❌ NameError: name 'my_varaible' is not defined
except NameError:
    print("Переменная не определена")

# Пример 2: Использование до объявления
try:
    print(x)  # ❌ NameError: name 'x' is not defined
    x = 10
except NameError:
    print("Переменная используется до определения")

# Пример 3: Удаленная переменная
try:
    y = 5
    del y
    print(y)  # ❌ NameError
except NameError:
    print("Переменная была удалена")
```

---

## 7. ZeroDivisionError - деление на ноль

**Когда возникает:** Деление на ноль

```python
# Пример 1: Простое деление
try:
    result = 10 / 0  # ❌ ZeroDivisionError
except ZeroDivisionError:
    print("Деление на ноль!")

# Пример 2: Целочисленное деление
try:
    result = 10 // 0  # ❌ ZeroDivisionError
except ZeroDivisionError:
    print("Деление на ноль!")

# Пример 3: Остаток от деления
try:
    result = 10 % 0  # ❌ ZeroDivisionError
except ZeroDivisionError:
    print("Деление на ноль!")

# Пример 4: Вычисление среднего
try:
    numbers = []
    average = sum(numbers) / len(numbers)  # ❌ ZeroDivisionError если список пуст
except ZeroDivisionError:
    print("Невозможно вычислить среднее для пустого списка")
    average = 0
```

**Правильная обработка:**
```python
# ✅ Проверка перед делением
def safe_divide(a, b):
    if b == 0:
        return None  # или float('inf'), или raise ValueError
    return a / b

# ✅ Для среднего
def average(numbers):
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)
```

---

## 8. FileNotFoundError - файл не найден

**Когда возникает:** Попытка открыть несуществующий файл

```python
# Пример 1: Открытие несуществующего файла
try:
    with open('nonexistent.txt', 'r') as f:
        content = f.read()
except FileNotFoundError:
    print("Файл не найден")

# Пример 2: Чтение с fallback
try:
    with open('config.txt', 'r') as f:
        config = f.read()
except FileNotFoundError:
    print("Используем конфигурацию по умолчанию")
    config = "default settings"

# Пример 3: Проверка перед открытием
from pathlib import Path

file_path = Path('data.txt')
if file_path.exists():
    with open(file_path, 'r') as f:
        data = f.read()
else:
    print("Файл не существует")
```

---

## 9. ImportError / ModuleNotFoundError - проблемы с импортом

**Когда возникает:** Модуль не найден или ошибка при импорте

```python
# Пример 1: Модуль не установлен
try:
    import some_package  # ❌ ModuleNotFoundError
except ModuleNotFoundError:
    print("Пакет не установлен. Установите: pip install some_package")

# Пример 2: Опциональная зависимость
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    print("Pandas не установлен, некоторые функции недоступны")

# Пример 3: Ошибка в самом модуле
try:
    from mymodule import broken_function
except ImportError as e:
    print(f"Ошибка импорта: {e}")
```

---

## 10. StopIteration - конец итератора

**Когда возникает:** Вызов next() на исчерпанном итераторе

```python
# Пример 1: Ручная работа с итератором
try:
    it = iter([1, 2, 3])
    print(next(it))  # 1
    print(next(it))  # 2
    print(next(it))  # 3
    print(next(it))  # ❌ StopIteration
except StopIteration:
    print("Итератор исчерпан")

# Пример 2: Безопасный next с default
it = iter([1, 2, 3])
value = next(it, None)  # Не вызовет StopIteration, вернет None

# Обычно StopIteration обрабатывается автоматически в циклах for
for item in [1, 2, 3]:  # StopIteration ловится неявно
    print(item)
```

---

## 11. AssertionError - проверка не прошла

**Когда возникает:** assert вернул False

```python
# Пример 1: Проверка условия
try:
    age = -5
    assert age >= 0, "Возраст не может быть отрицательным"  # ❌ AssertionError
except AssertionError as e:
    print(f"Ошибка проверки: {e}")

# Пример 2: Проверка типа
try:
    value = "123"
    assert isinstance(value, int), "Ожидалось число"  # ❌ AssertionError
except AssertionError as e:
    print(f"Неверный тип: {e}")

# ⚠️ Важно: assert отключается флагом -O (optimize)
# Не используйте assert для валидации пользовательского ввода!
# Используйте явные проверки с ValueError/TypeError
```

---

## 12. RecursionError - слишком глубокая рекурсия

**Когда возникает:** Превышен лимит рекурсии (обычно ~1000 вызовов)

```python
# Пример 1: Бесконечная рекурсия
def infinite_recursion():
    return infinite_recursion()  # ❌ RecursionError

try:
    infinite_recursion()
except RecursionError:
    print("Превышен лимит рекурсии")

# Пример 2: Слишком глубокая рекурсия
def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)

try:
    result = factorial(3000)  # ❌ RecursionError
except RecursionError:
    print("Слишком большое число для рекурсивного вычисления")

# ✅ Решение: используйте итеративный подход
def factorial_iterative(n):
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
```

---

## Комплексный пример: обработка нескольких исключений

```python
def process_user_data(user_id):
    """Комплексная обработка данных пользователя"""
    try:
        # Может вызвать ValueError если user_id не число
        uid = int(user_id)
        
        # Может вызвать KeyError если пользователь не найден
        user_data = database[uid]
        
        # Может вызвать IndexError если список пуст
        first_order = user_data['orders'][0]
        
        # Может вызвать TypeError при вычислениях
        total = sum(order['price'] for order in user_data['orders'])
        
        # Может вызвать ZeroDivisionError
        average = total / len(user_data['orders'])
        
        return {
            'user': user_data['name'],
            'first_order': first_order,
            'average': average
        }
        
    except ValueError:
        print("❌ Неверный формат ID пользователя")
        return None
        
    except KeyError as e:
        print(f"❌ Пользователь {user_id} не найден или отсутствует поле {e}")
        return None
        
    except IndexError:
        print("❌ У пользователя нет заказов")
        return None
        
    except (TypeError, AttributeError) as e:
        print(f"❌ Ошибка в структуре данных: {e}")
        return None
        
    except ZeroDivisionError:
        print("❌ Деление на ноль при вычислении среднего")
        return None
        
    except Exception as e:
        # Ловим всё остальное (неожиданные ошибки)
        print(f"❌ Неожиданная ошибка: {type(e).__name__}: {e}")
        return None
```

---

## Правила хорошего тона

### ✅ Делайте так:

```python
# 1. Ловите конкретные исключения
try:
    value = int(input())
except ValueError:  # ✅ Конкретное исключение
    print("Не число")

# 2. Используйте "as" для доступа к сообщению
try:
    risky_operation()
except ValueError as e:  # ✅
    print(f"Ошибка: {e}")

# 3. Несколько исключений с одной обработкой
try:
    process()
except (ValueError, TypeError) as e:  # ✅
    print(f"Ошибка типа или значения: {e}")

# 4. Exception в конце (catch-all)
try:
    complex_operation()
except ValueError:
    handle_value_error()
except KeyError:
    handle_key_error()
except Exception as e:  # ✅ Всё остальное
    log_unexpected_error(e)
```

### ❌ Не делайте так:

```python
# 1. Голый except (ловит ВСЁ, даже Ctrl+C!)
try:
    something()
except:  # ❌ Слишком широко
    pass

# 2. Игнорирование исключений
try:
    important_operation()
except Exception:
    pass  # ❌ "Проглотили" ошибку, не логируем

# 3. Слишком широкий try блок
try:  # ❌ Сложно понять где ошибка
    a = get_a()
    b = get_b()
    c = get_c()
    d = process(a, b, c)
except ValueError:
    # Какая операция вызвала ошибку?
    pass
```

---

## Быстрая шпаргалка для лайвкодинга

| Исключение | Когда ловить |
|-----------|--------------|
| `ValueError` | Конвертация типов, неверные значения |
| `KeyError` | Доступ к словарю по отсутствующему ключу |
| `IndexError` | Индекс за пределами списка |
| `TypeError` | Операции с неправильными типами |
| `AttributeError` | Обращение к несуществующему атрибуту |
| `NameError` | Использование необъявленной переменной |
| `ZeroDivisionError` | Деление на ноль |
| `FileNotFoundError` | Файл не найден |
| `ImportError` | Проблемы с импортом модуля |
| `StopIteration` | Итератор исчерпан |
| `RecursionError` | Слишком глубокая рекурсия |
| `Exception` | Любое другое исключение (catch-all) |

**Помните:** Всегда ловите `Exception`, а не `BaseException` - иначе перехватите системные сигналы!

---

## Перед собеседованием - проверьте себя:

- [ ] Знаю разницу между `ValueError` и `TypeError`
- [ ] Помню что `KeyError` для словарей, `IndexError` для списков
- [ ] Знаю что `Exception` - catch-all для обычных ошибок
- [ ] Понимаю когда использовать `.get()` вместо `try/except KeyError`
- [ ] Помню что `except:` без указания типа - плохая практика
- [ ] Знаю как обработать несколько исключений одновременно
- [ ] Помню про `as e` для доступа к сообщению об ошибке
