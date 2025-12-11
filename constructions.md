# Шпаргалка: Основные Python конструкции для собеседований

## 1. Декораторы

### Простой декоратор (без параметров)
```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("До вызова функции")
        result = func(*args, **kwargs)
        print("После вызова функции")
        return result
    return wrapper

@my_decorator
def say_hello(name):
    print(f"Hello, {name}")
```

**Как это работает изнутри:**
1. Python видит `@my_decorator` над функцией
2. Эквивалентно: `say_hello = my_decorator(say_hello)`
3. Теперь `say_hello` указывает на `wrapper`, а не на оригинальную функцию
4. При вызове `say_hello("Alice")` выполняется `wrapper("Alice")`

**Частые ошибки:**
❌ Забыть `return result` в wrapper - функция вернет None
❌ Не использовать `*args, **kwargs` - декоратор не будет универсальным
❌ Вызвать декоратор со скобками когда не нужно: `@my_decorator()`

### Декоратор с параметрами (фабрика декораторов)
```python
def repeat(times):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(times=3)
def greet(name):
    print(f"Hello, {name}")
```

**Как это работает изнутри:**
1. Python видит `@repeat(times=3)` - вызывает функцию `repeat(3)`
2. `repeat(3)` возвращает `decorator` (средний уровень)
3. Эквивалентно: `greet = repeat(3)(greet)`
4. Разбор по шагам:
   - `repeat(3)` → возвращает функцию `decorator`
   - `decorator(greet)` → возвращает функцию `wrapper`
   - Теперь `greet` указывает на `wrapper`

**Порядок выполнения:**
```
@repeat(times=3)          # Шаг 1: вызывается repeat(3)
                          # Возвращается decorator
def greet(name):          # Шаг 2: decorator(greet) вызывается
    ...                   # Возвращается wrapper
                          # greet теперь = wrapper
```

**Частые ошибки:**
❌ Забыть средний уровень (decorator) - декоратор не будет работать
❌ Перепутать порядок: параметры → функция → аргументы функции
❌ Вернуть `func` вместо `wrapper` на среднем уровне

### Декоратор с сохранением метаданных
```python
from functools import wraps

def my_decorator(func):
    @wraps(func)  # Сохраняет __name__, __doc__ и т.д.
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
```

**Зачем нужен @wraps:**
Без него декорированная функция теряет свои метаданные:
```python
# БЕЗ @wraps
def my_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def greet(name):
    """Greets a person"""
    pass

print(greet.__name__)  # 'wrapper' ❌
print(greet.__doc__)   # None ❌

# С @wraps
print(greet.__name__)  # 'greet' ✅
print(greet.__doc__)   # 'Greets a person' ✅
```

**Частые ошибки:**
❌ Забыть импортировать `wraps` из functools
❌ Применить @wraps к неправильной функции (должна быть на wrapper)

### Класс-декоратор
```python
class CountCalls:
    def __init__(self, func):
        self.func = func
        self.count = 0
    
    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"Вызов #{self.count}")
        return self.func(*args, **kwargs)

@CountCalls
def say_hello():
    print("Hello!")
```

## 2. Context Managers (менеджеры контекста)

### Через класс
```python
class FileManager:
    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode
        self.file = None
    
    def __enter__(self):
        self.file = open(self.filename, self.mode)
        return self.file
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()
        # Возвращаем False, чтобы не подавлять исключения
        return False

# Использование
with FileManager('test.txt', 'w') as f:
    f.write('Hello')
```

**Как это работает изнутри:**
1. `with FileManager(...) as f:` вызывает `__enter__()`
2. Возвращаемое значение `__enter__()` присваивается в `f`
3. Выполняется блок кода внутри with
4. После блока (или при ошибке) вызывается `__exit__()`
5. Параметры `__exit__`: тип исключения, значение, traceback (или None если всё ок)

**Порядок выполнения:**
```python
# 1. Создается объект FileManager
# 2. Вызывается __enter__() → возвращается file
# 3. file присваивается в f
# 4. Выполняется код в блоке
# 5. Вызывается __exit__() (даже если была ошибка)
```

**Частые ошибки:**
❌ Забыть `return` в `__enter__()` - в `f` будет None
❌ Не проверить что `self.file` существует в `__exit__()`
❌ Вернуть `True` из `__exit__()` - исключение будет подавлено (обычно не нужно)
❌ Не обработать случай, когда `__enter__()` упал до создания ресурса

### Через генератор (contextlib)
```python
from contextlib import contextmanager

@contextmanager
def file_manager(filename, mode):
    file = open(filename, mode)
    try:
        yield file
    finally:
        file.close()

# Использование
with file_manager('test.txt', 'w') as f:
    f.write('Hello')
```

**Как это работает изнутри:**
1. Функция выполняется до `yield`
2. Значение после `yield` возвращается в блок `with`
3. Выполняется код внутри `with`
4. После блока выполнение возвращается после `yield`
5. `finally` гарантирует очистку даже при ошибке

**Частые ошибки:**
❌ Забыть `try/finally` - ресурс не закроется при ошибке
❌ Использовать `return` вместо `yield`
❌ Использовать несколько `yield` - работает только один

## 3. Генераторы

### Функция-генератор
```python
def countdown(n):
    while n > 0:
        yield n
        n -= 1

# Использование
for num in countdown(5):
    print(num)
```

**Как это работает изнутри:**
1. При вызове `countdown(5)` функция НЕ выполняется
2. Возвращается объект-генератор
3. При каждом вызове `next()` (в цикле for) функция выполняется до `yield`
4. `yield` возвращает значение и "замораживает" выполнение
5. При следующем `next()` выполнение продолжается после `yield`
6. Когда функция заканчивается → выбрасывается `StopIteration`

**Состояние между вызовами:**
```python
gen = countdown(3)
print(next(gen))  # 3 - выполнение до yield, n становится 2
print(next(gen))  # 2 - продолжение, n становится 1
print(next(gen))  # 1 - продолжение, n становится 0
print(next(gen))  # StopIteration - while не выполнился
```

**Частые ошибки:**
❌ Забыть что генератор можно пройти только один раз
❌ Пытаться использовать `return` для возврата значений (используйте `yield`)
❌ Не понимать что функция не выполняется до первого `next()`

### Generator expression
```python
# Вместо list comprehension для экономии памяти
squares = (x**2 for x in range(1000000))
```

**Разница с list comprehension:**
```python
# List comprehension - создает весь список в памяти
list_comp = [x**2 for x in range(1000000)]  # ~8 MB памяти

# Generator expression - вычисляет по требованию
gen_exp = (x**2 for x in range(1000000))    # ~200 bytes

# Но можно пройти только один раз!
print(sum(gen_exp))  # Работает
print(sum(gen_exp))  # 0 - генератор исчерпан!
```

**Частые ошибки:**
❌ Пытаться обратиться по индексу: `gen_exp[0]` - не работает
❌ Пытаться получить длину: `len(gen_exp)` - не работает
❌ Использовать повторно - генератор одноразовый

### Генератор с send()
```python
def accumulator():
    total = 0
    while True:
        value = yield total
        if value is not None:
            total += value

acc = accumulator()
next(acc)  # Инициализация
print(acc.send(5))   # 5
print(acc.send(10))  # 15
```

## 4. Дескрипторы

### Базовый дескриптор
```python
class Descriptor:
    def __init__(self, name):
        self.name = name
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj.__dict__.get(self.name)
    
    def __set__(self, obj, value):
        obj.__dict__[self.name] = value
    
    def __delete__(self, obj):
        del obj.__dict__[self.name]

class MyClass:
    attr = Descriptor('attr')
```

**Как это работает изнутри:**
```python
class MyClass:
    attr = Descriptor('_attr')  # Создается ОДИН объект дескриптора

obj1 = MyClass()
obj2 = MyClass()

# obj1.attr = 5
# Python видит что attr это дескриптор
# Вызывает: MyClass.attr.__set__(obj1, 5)
# Сохраняет в obj1.__dict__['_attr'] = 5

# print(obj1.attr)
# Python видит что attr это дескриптор
# Вызывает: MyClass.attr.__get__(obj1, MyClass)
# Возвращает obj1.__dict__['_attr']
```

**Критически важно понимать:**
1. Дескриптор - это ОДИН объект на уровне класса
2. Он обрабатывает доступ к атрибуту для ВСЕХ экземпляров
3. Поэтому данные должны храниться в `obj.__dict__`, а не в `self`

**Неправильно:**
```python
class WrongDescriptor:
    def __get__(self, obj, objtype=None):
        return self.value  # ❌ Одно значение на ВСЕ объекты!
    
    def __set__(self, obj, value):
        self.value = value  # ❌
```

**Правильно:**
```python
class CorrectDescriptor:
    def __init__(self, name):
        self.name = name
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj.__dict__[self.name]  # ✅ Данные в объекте
    
    def __set__(self, obj, value):
        obj.__dict__[self.name] = value  # ✅
```

**Проверка `if obj is None`:**
Когда вызывается через класс, а не экземпляр:
```python
MyClass.attr  # obj=None, objtype=MyClass
obj.attr      # obj=экземпляр, objtype=MyClass
```

**Частые ошибки:**
❌ Хранить данные в дескрипторе (`self.value`) вместо объекта
❌ Забыть проверку `if obj is None`
❌ Не понимать что дескриптор один на все экземпляры

### Валидирующий дескриптор
```python
class PositiveNumber:
    def __init__(self, name):
        self.name = name
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj.__dict__.get(self.name, 0)
    
    def __set__(self, obj, value):
        if value < 0:
            raise ValueError(f"{self.name} must be positive")
        obj.__dict__[self.name] = value

class Product:
    price = PositiveNumber('price')
```

## 5. Property

### Классический способ
```python
class Circle:
    def __init__(self, radius):
        self._radius = radius
    
    @property
    def radius(self):
        return self._radius
    
    @radius.setter
    def radius(self, value):
        if value < 0:
            raise ValueError("Radius cannot be negative")
        self._radius = value
    
    @radius.deleter
    def radius(self):
        del self._radius
    
    @property
    def area(self):
        return 3.14 * self._radius ** 2
```

**Как это работает изнутри:**
1. `@property` превращает метод в дескриптор
2. При доступе `circle.radius` вызывается getter
3. При присваивании `circle.radius = 5` вызывается setter
4. При `del circle.radius` вызывается deleter
5. Это синтаксический сахар над дескрипторами

**Порядок выполнения:**
```python
c = Circle(5)
print(c.radius)      # Вызов: radius.__get__(c, Circle) → getter
c.radius = 10        # Вызов: radius.__set__(c, 10) → setter
del c.radius         # Вызов: radius.__delete__(c) → deleter
```

**Зачем нужно:**
- Инкапсуляция: скрыть внутреннее представление
- Валидация: проверить значение перед установкой
- Вычисляемые атрибуты: area вычисляется каждый раз
- Обратная совместимость: превратить атрибут в свойство без изменения API

**Частые ошибки:**
❌ Забыть подчеркивание в `_radius` - рекурсия в setter
```python
@radius.setter
def radius(self, value):
    self.radius = value  # ❌ Бесконечная рекурсия!
    self._radius = value # ✅ Правильно
```
❌ Использовать разные имена для getter и setter
❌ Сделать setter без getter (можно, но странно)

## 6. Метаклассы

### Простой метакласс
```python
class Meta(type):
    def __new__(mcs, name, bases, attrs):
        # Добавляем метод ко всем классам
        attrs['get_class_name'] = lambda self: name
        return super().__new__(mcs, name, bases, attrs)

class MyClass(metaclass=Meta):
    pass

obj = MyClass()
print(obj.get_class_name())  # MyClass
```

**Как это работает изнутри:**
```python
# Обычное создание класса:
class MyClass:
    x = 5

# Под капотом Python делает примерно это:
MyClass = type('MyClass', (), {'x': 5})

# С метаклассом:
class MyClass(metaclass=Meta):
    x = 5

# Python делает:
MyClass = Meta('MyClass', (), {'x': 5})
```

**Порядок выполнения:**
1. Python собирает все атрибуты класса в словарь `attrs`
2. Вызывает `Meta.__new__(mcs, 'MyClass', (), attrs)`
3. `__new__` может изменить `attrs` перед созданием класса
4. `super().__new__()` создает класс
5. (Опционально) `Meta.__init__` может настроить созданный класс

**Методы метакласса:**
- `__new__` - создает класс (вызывается до создания)
- `__init__` - инициализирует класс (вызывается после создания)
- `__call__` - вызывается при создании экземпляра класса

**Что можно делать:**
- Автоматически регистрировать классы
- Валидировать структуру класса
- Добавлять/изменять методы и атрибуты
- Реализовать паттерны (Singleton, Registry)

**Частые ошибки:**
❌ Использовать метаклассы когда достаточно декоратора класса
❌ Забыть вызвать `super().__new__()` - класс не создастся
❌ Путать параметры: `mcs` (метакласс), `name` (имя класса), `bases` (родители), `attrs` (атрибуты)

### Singleton через метакласс
```python
class SingletonMeta(type):
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Database(metaclass=SingletonMeta):
    def __init__(self):
        print("Инициализация БД")
```

## 7. Магические методы

### Арифметические операции
```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)
    
    def __repr__(self):
        return f"Vector({self.x}, {self.y})"
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
```

**Как это работает изнутри:**
```python
v1 = Vector(1, 2)
v2 = Vector(3, 4)

v1 + v2  # Python вызывает v1.__add__(v2)
v1 - v2  # Python вызывает v1.__sub__(v2)
v1 * 5   # Python вызывает v1.__mul__(5)
v1 == v2 # Python вызывает v1.__eq__(v2)
```

**Важные пары методов:**
- `__add__` и `__radd__` (правая версия: когда левый операнд не поддерживает операцию)
- `__eq__` и `__ne__` (равно/не равно)
- `__lt__`, `__le__`, `__gt__`, `__ge__` (сравнения)
- `__str__` (для пользователя) и `__repr__` (для разработчика)

**Частые ошибки:**
❌ Изменять `self` вместо создания нового объекта
```python
def __add__(self, other):
    self.x += other.x  # ❌ Меняем оригинал!
    return self
```
❌ Забыть `return` в арифметических операциях
❌ Не обработать случай когда `other` не того типа
```python
def __add__(self, other):
    if not isinstance(other, Vector):
        return NotImplemented  # Правильный способ
    return Vector(self.x + other.x, self.y + other.y)
```

### Контейнерные методы
```python
class MyList:
    def __init__(self):
        self.items = []
    
    def __len__(self):
        return len(self.items)
    
    def __getitem__(self, index):
        return self.items[index]
    
    def __setitem__(self, index, value):
        self.items[index] = value
    
    def __delitem__(self, index):
        del self.items[index]
    
    def __contains__(self, item):
        return item in self.items
    
    def __iter__(self):
        return iter(self.items)
```

**Как это работает изнутри:**
```python
ml = MyList()
ml.items = [1, 2, 3]

len(ml)       # Python вызывает ml.__len__()
ml[0]         # Python вызывает ml.__getitem__(0)
ml[0] = 5     # Python вызывает ml.__setitem__(0, 5)
del ml[0]     # Python вызывает ml.__delitem__(0)
1 in ml       # Python вызывает ml.__contains__(1)
for x in ml:  # Python вызывает ml.__iter__()
```

**Бонус - срезы:**
```python
def __getitem__(self, key):
    if isinstance(key, slice):
        # key.start, key.stop, key.step
        return self.items[key]
    return self.items[key]

ml[1:3]  # key будет slice(1, 3, None)
```

**Частые ошибки:**
❌ Не поддерживать срезы в `__getitem__`
❌ Не проверять границы индексов
❌ Реализовать `__getitem__` но забыть `__len__` - некоторые функции не будут работать

## 8. Callable объекты

### Функтор (класс с __call__)
```python
class Multiplier:
    def __init__(self, factor):
        self.factor = factor
    
    def __call__(self, x):
        return x * self.factor

double = Multiplier(2)
print(double(5))  # 10
```

## 9. Итераторы

### Кастомный итератор
```python
class Countdown:
    def __init__(self, start):
        self.current = start
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        self.current -= 1
        return self.current + 1

# Использование
for num in Countdown(5):
    print(num)
```

**Как это работает изнутри:**
1. `for` вызывает `__iter__()` на объекте → получает итератор
2. В цикле многократно вызывается `__next__()` на итераторе
3. Когда `__next__()` выбрасывает `StopIteration` - цикл останавливается

**Важное различие:**
```python
# Iterable (итерируемый) - имеет __iter__()
# Iterator (итератор) - имеет __iter__() и __next__()

# Часто итератор возвращает сам себя из __iter__():
def __iter__(self):
    return self  # Я и есть итератор!

# Но можно разделить:
class CountdownIterable:
    def __init__(self, start):
        self.start = start
    
    def __iter__(self):
        return CountdownIterator(self.start)  # Создаем новый итератор

class CountdownIterator:
    def __init__(self, start):
        self.current = start
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        self.current -= 1
        return self.current + 1

# Плюс разделения: можно пройти несколько раз
cd = CountdownIterable(3)
for n in cd:
    print(n)  # 3, 2, 1
for n in cd:
    print(n)  # 3, 2, 1 снова!
```

**Частые ошибки:**
❌ Забыть `raise StopIteration` - бесконечный цикл
❌ Возвращать `None` вместо `raise StopIteration`
❌ Изменять состояние в `__iter__()` вместо `__next__()`
❌ Не понимать что итератор обычно одноразовый

## 10. Абстрактные классы

### Через ABC (Abstract Base Class)
```python
from abc import ABC, abstractmethod

class Animal(ABC):
    @abstractmethod
    def make_sound(self):
        pass
    
    @abstractmethod
    def move(self):
        pass
    
    def description(self):
        return "I am an animal"

class Dog(Animal):
    def make_sound(self):
        return "Woof!"
    
    def move(self):
        return "Running"
```

## 11. Множественное наследование и MRO

### Миксины
```python
class LoggerMixin:
    def log(self, message):
        print(f"[LOG] {message}")

class TimestampMixin:
    def get_timestamp(self):
        from datetime import datetime
        return datetime.now()

class User(LoggerMixin, TimestampMixin):
    def __init__(self, name):
        self.name = name
    
    def do_something(self):
        self.log(f"{self.name} did something at {self.get_timestamp()}")
```

**Как работает MRO (Method Resolution Order):**
Python использует алгоритм C3 linearization для определения порядка поиска методов.

```python
class A:
    def method(self):
        print("A")

class B(A):
    def method(self):
        print("B")

class C(A):
    def method(self):
        print("C")

class D(B, C):
    def method(self):
        print("D")
        super().method()

print(D.__mro__)
# (<class 'D'>, <class 'B'>, <class 'C'>, <class 'A'>, <class 'object'>)

d = D()
d.method()
# Выведет: D B C A
```

**Почему такой порядок:**
1. Сначала сам класс `D`
2. Потом родители слева направо `B`, `C`
3. Потом их общий родитель `A`
4. В конце базовый `object`

**Правила MRO:**
- Класс всегда перед родителями
- Порядок родителей сохраняется (слева направо)
- Родитель появляется только после всех своих потомков

### Diamond problem
```python
class A:
    def method(self):
        print("A")

class B(A):
    def method(self):
        print("B")
        super().method()

class C(A):
    def method(self):
        print("C")
        super().method()

class D(B, C):
    def method(self):
        print("D")
        super().method()

d = D()
d.method()
# Выведет: D B C A (порядок по MRO)
print(D.__mro__)  # Показывает порядок разрешения методов
```

**Почему super() работает правильно:**
`super()` НЕ вызывает метод родительского класса!
Он вызывает следующий метод в MRO.

```python
# В D.method():
super().method()  # Вызовет B.method (следующий в MRO)

# В B.method():
super().method()  # Вызовет C.method (следующий в MRO)

# В C.method():
super().method()  # Вызовет A.method (следующий в MRO)
```

**Без super() был бы дубль вызова A:**
```python
class B(A):
    def method(self):
        print("B")
        A.method(self)  # ❌ Явный вызов

class C(A):
    def method(self):
        print("C")
        A.method(self)  # ❌ Явный вызов

# A.method() вызовется дважды!
```

**Частые ошибки:**
❌ Думать что `super()` вызывает метод родителя (на самом деле следующий в MRO)
❌ Не использовать `super()` в множественном наследовании - некоторые методы не вызовутся
❌ Миксины с `__init__` без `super().__init__()` - сломает цепочку инициализации
❌ Изменять сигнатуры методов в цепочке наследования

## 12. Замыкания (Closures)

```python
def outer(x):
    def inner(y):
        return x + y
    return inner

add_5 = outer(5)
print(add_5(3))  # 8
```

**Как это работает изнутри:**
1. `outer(5)` вызывается, `x = 5`
2. Создается функция `inner`, которая "захватывает" `x` из области видимости `outer`
3. `outer` возвращает `inner`
4. Даже после завершения `outer`, `inner` сохраняет доступ к `x`
5. Это называется "замыкание" - функция + захваченные переменные

**Что происходит в памяти:**
```python
add_5 = outer(5)
# add_5.__closure__ содержит ячейки с захваченными переменными
print(add_5.__closure__)  # (<cell at 0x...: int object at 0x...>,)
print(add_5.__closure__[0].cell_contents)  # 5
```

### С nonlocal
```python
def counter():
    count = 0
    
    def increment():
        nonlocal count
        count += 1
        return count
    
    return increment

c = counter()
print(c())  # 1
print(c())  # 2
```

**Зачем нужен nonlocal:**
```python
# БЕЗ nonlocal - ошибка
def counter():
    count = 0
    def increment():
        count += 1  # ❌ UnboundLocalError!
        # Python думает что count локальная переменная
        # но мы пытаемся читать её до присваивания
        return count
    return increment

# С nonlocal - работает
def counter():
    count = 0
    def increment():
        nonlocal count  # ✅ Говорим что count из внешней области
        count += 1
        return count
    return increment
```

**Важное различие:**
- `global` - ссылка на переменную модуля (глобальную)
- `nonlocal` - ссылка на переменную из объемлющей функции

**Частые ошибки:**
❌ Забыть `nonlocal` при изменении переменной из внешней области
❌ Использовать `global` вместо `nonlocal`
❌ Пытаться использовать `nonlocal` на глобальном уровне (только внутри функций)

## 13. Функции высшего порядка

### Map, filter, reduce
```python
from functools import reduce

numbers = [1, 2, 3, 4, 5]

# Map
squared = list(map(lambda x: x**2, numbers))

# Filter
evens = list(filter(lambda x: x % 2 == 0, numbers))

# Reduce
sum_all = reduce(lambda x, y: x + y, numbers)
```

### Partial functions
```python
from functools import partial

def power(base, exponent):
    return base ** exponent

square = partial(power, exponent=2)
cube = partial(power, exponent=3)

print(square(5))  # 25
print(cube(3))    # 27
```

## 14. Кастомные исключения

```python
class ValidationError(Exception):
    def __init__(self, field, message):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")

class AgeValidationError(ValidationError):
    def __init__(self, age):
        super().__init__('age', f"Invalid age: {age}")

# Использование
def validate_age(age):
    if age < 0 or age > 150:
        raise AgeValidationError(age)
```

## 15. Slots (оптимизация памяти)

```python
class Point:
    __slots__ = ['x', 'y']  # Только эти атрибуты разрешены
    
    def __init__(self, x, y):
        self.x = x
        self.y = y

# Экономит память, но нельзя добавлять новые атрибуты
p = Point(1, 2)
# p.z = 3  # Вызовет AttributeError
```

## 16. Async конструкции (базово)

### Async generator
```python
async def async_countdown(n):
    while n > 0:
        yield n
        n -= 1
        await asyncio.sleep(0.1)

# Использование
async def main():
    async for num in async_countdown(5):
        print(num)
```

### Async context manager
```python
class AsyncResource:
    async def __aenter__(self):
        print("Acquiring resource")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print("Releasing resource")
        return False

# Использование
async def main():
    async with AsyncResource() as resource:
        print("Using resource")
```

## Как учить

1. **Выберите 5-7 самых частых конструкций** для вашего уровня (декораторы, context managers, property, генераторы, magic methods)

2. **Для каждой напишите 2-3 раза с нуля** без подсматривания

3. **Объясните вслух** как это работает, что куда передается

4. **На следующий день** - проверьте, помните ли еще, если нет - повторите

5. **Перед собеседованием** - быстро пробегитесь по шпаргалке за 15 минут

---

## Быстрая проверка понимания

Если можете ответить на эти вопросы - вы готовы:

**Декораторы:**
- Чем отличается `@decorator` от `@decorator()`?
- Почему нужны три уровня функций в декораторе с параметрами?
- Зачем нужен `@wraps`?

**Context managers:**
- Что вернет `__enter__()`? Куда попадет это значение?
- Когда вызовется `__exit__()`? Что означает его return True?
- В чем разница между `try/finally` и контекстным менеджером?

**Property:**
- Почему нужно подчеркивание в `self._radius`?
- Можно ли сделать read-only property? Как?

**Генераторы:**
- Когда выполняется код функции-генератора?
- Можно ли пройти генератор дважды?
- Чем `yield` отличается от `return`?

**Дескрипторы:**
- Почему дескриптор один на все экземпляры класса?
- Где хранятся данные - в дескрипторе или в объекте?
- Что такое `if obj is None`?

**MRO:**
- Что вызовет `super()` - родительский класс?
- Почему `super()` решает проблему diamond?
- Как посмотреть порядок разрешения методов?

---

## Приоритет для мидла

**ОБЯЗАТЕЛЬНО знать:**
- ✅ Декораторы (с параметрами и без)
- ✅ Context managers (оба способа)
- ✅ Property (getter/setter)
- ✅ Генераторы (yield)
- ✅ Базовые magic methods (__init__, __str__, __repr__, __eq__)

**Желательно знать:**
- ⭐ Итераторы (__iter__, __next__)
- ⭐ Дескрипторы (базово)
- ⭐ Замыкания и nonlocal
- ⭐ Абстрактные классы (ABC)

**Плюсом будет:**
- 💡 Метаклассы (базовое понимание)
- 💡 Множественное наследование и MRO
- 💡 Slots
- 💡 Async конструкции
