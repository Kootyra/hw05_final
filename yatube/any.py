'''
from posts.models import Post
from django.db import connection

keyword = 'вечер'
posts = Post.objects.select_related('author', 'group').filter(text__contains=keyword)

for post in posts:
    print(f'{post.text} Автор: {post.author.get_full_name}, Дата публикации: {post.pub_date}, Группа: {post.group}')

for query in connection.queries:
    print(query['sql'])



def uglify(value):
    st = ''
    for c, x in enumerate(value):
        if c % 2 != 0:
            st = st + x.upper()
        else:
            st = st + x.lower()
    print(st)


uglify('Как дела на этом свете')





def cache3(func):
    cache = {'result': None, 'counter': 0}
    def wrapper(*args, **kwargs):
        if cache['counter'] == 0 or cache['counter'] == 3:
            cache['result'] = func(*args, **kwargs)
            cache['counter'] = 1
            return cache['result']
        elif cache['counter'] < 3:
            cache['counter'] += 1
            return cache['result']
    return wrapper


@cache3
def heavy():
    print('Сложные вычисления')
    return 1


print(heavy())
# Сложные вычисления
# 1
print(heavy())
# 1
print(heavy())
# 1

# Опять кеш устарел, надо вычислять заново
print(heavy())
# Сложные вычисления
# 1
print(heavy())
print(heavy())
print(heavy())
print(heavy())
print(heavy())
print(heavy())
print(heavy())
print(heavy())
print(heavy())




from datetime import datetime

def year():
    """Добавляет переменную с текущим годом."""
    return {
        f'© { datetime.now().year } Copyright'
    }
print(year())


def movie_quotes(name):
    """Возвращает цитаты известных персонажей из фильмов

    >>> movie_quotes('Элли')
    'Тото, у меня такое ощущение, что мы не в Канзасе!'

    >>> movie_quotes('Шерлок')
    'Элементарно, Ватсон!'

    >>> movie_quotes('Дарт Вейдер')
    'Люк, я — твой отец.'

    >>> movie_quotes('Леонид Тощев')
    'Персонаж пока не известен миллионам.'
    """
    quotes = {
        'Элли': 'Тото, у меня такое ощущение, что мы не в Канзасе!',
        'Шерлок': 'Элементарно, !',
        'Дарт Вейдер': 'Люк, я — твой отец.',
    }
    if __name__ == '__main__':
        import doctest
        doctest.testmod() 
    return quotes.get(name, 'Персонаж пока не известен миллионам.') 
'''
import unittest


def setUpModule():
    """Вызывается один раз перед всеми классами, которые есть в файле."""
    print('> setUpModule')


def tearDownModule():
    """Вызывается один раз после всех классов, которые есть в файле."""
    print('> tearDownModule')


class TestExample(unittest.TestCase):
    """Демонстрирует принцип работы тестов."""

    @classmethod
    def setUpClass(cls):
        """Вызывается один раз перед запуском всех тестов класса."""
        print('>> setUpClass')

    @classmethod
    def tearDownClass(cls):
        """Вызывается один раз после запуска всех тестов класса."""
        print('>> tearDownClass')

    def setUp(self):
        """Подготовка прогона теста. Вызывается перед каждым тестом."""
        print('>>> setUp')

    def tearDown(self):
        """Вызывается после каждого теста."""
        print('>>> tearDown')

    def test_one(self): # это -- test case 
        print('>>>> test_simple')

    def test_one_more(self): # это -- ещё один test case
        print('>>>> test_simple')


if __name__ == '__main__':
    unittest.main()