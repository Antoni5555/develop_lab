import pytest

from core.templatetags.plural import plural, plural_word


@pytest.mark.parametrize('number, expected', [
    (1, '1 задача'), (2, '2 задачи'), (4, '4 задачи'), (5, '5 задач'),
    (11, '11 задач'), (12, '12 задач'), (21, '21 задача'), (22, '22 задачи'),
    (0, '0 задач'), (111, '111 задач'),
])
def test_plural(number, expected):
    assert plural(number, 'задача,задачи,задач') == expected


def test_plural_word():
    assert plural_word(3, 'курс,курса,курсов') == 'курса'
