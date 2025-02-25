import pytest
from http import HTTPStatus
from pytest_django.asserts import assertRedirects

from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    [
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('id_for_args')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None)
    ]
)
def test_home_availability_for_anonymous_user(client, name, args):
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


# Добавляем к тесту ещё один декоратор parametrize; в его параметры
# нужно передать фикстуры-клиенты и ожидаемый код ответа для каждого клиента.
# @pytest.mark.parametrize(
#     # parametrized_client - название параметра,
#     # в который будут передаваться фикстуры;
#     # Параметр expected_status - ожидаемый статус ответа.
#     'parametrized_client, expected_status',
#     # В кортеже с кортежами передаём значения для параметров:
#     (
#         ('not_author_client', HTTPStatus.NOT_FOUND),
#         ('author_client', HTTPStatus.OK)
#     ),
# )
# # Этот декоратор оставляем таким же, как в предыдущем тесте.
# @pytest.mark.parametrize(
#     'name',
#     ('notes:detail', 'notes:edit', 'notes:delete'),
# )
# # В параметры теста добавляем имена parametrized_client и expected_status.
# def test_pages_availability_for_different_users(
#         parametrized_client, name, note, expected_status
# ):
#     url = reverse(name, args=(note.slug,))
#     # Делаем запрос от имени клиента parametrized_client:
#     response = parametrized_client.get(url)
#     # Ожидаем ответ страницы, указанный в expected_status:
#     assert response.status_code == expected_status


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    # Предварительно оборачиваем имена фикстур
    # в вызов функции pytest.lazy_fixture().
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:detail', 'news:edit', 'news:delete'),
)
def test_pages_availability_for_author(
        parametrized_client, name, comment, expected_status
):
    url = reverse(name, args=(comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    # Вторым параметром передаём note_object,
    # в котором будет либо фикстура с объектом заметки, либо None.
    'name, note_object',
    (
        ('notes:detail', pytest.lazy_fixture('note')),
        ('notes:edit', pytest.lazy_fixture('note')),
        ('notes:delete', pytest.lazy_fixture('note')),
        ('notes:add', None),
        ('notes:success', None),
        ('notes:list', None),
    ),
)
# Передаём в тест анонимный клиент, name проверяемых страниц и note_object:
def test_redirects(client, name, note_object):
    login_url = reverse('users:login')
    # Формируем URL в зависимости от того, передан ли объект заметки:
    if note_object is not None:
        url = reverse(name, args=(note_object.slug,))
    else:
        url = reverse(name)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    # Ожидаем, что со всех проверяемых страниц анонимный клиент
    # будет перенаправлен на страницу логина:
    assertRedirects(response, expected_url)
