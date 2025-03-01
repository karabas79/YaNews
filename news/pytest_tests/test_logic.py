from http import HTTPStatus
import pdb
import pytest
from pytest_django.asserts import assertRedirects, assertFormError
from pytils.translit import slugify

from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import News, Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, detail_url, form_data):
    url = detail_url
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    # pdb.set_trace()
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


# @pytest.mark.django_db
def test_authorized_user_can_create_comment(
    author_client,
    author,
    detail_url,
    form_data,
    news
):
    """Проверяет, что авторизованный пользователь может создать комментарий."""
    # Совершаем POST-запрос через авторизованный клиент.
    url = detail_url
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    assert response.url == f'{url}#comments'  # Проверяем URL редиректа
    new_comment = Comment.objects.get()

    assert new_comment.text == form_data['text']
    assert new_comment.news == news
    assert new_comment.author == author


def test_user_cant_use_bad_words(author_client, detail_url, form_data):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    # Отправляем запрос через авторизованный клиент.
    response = author_client.post(detail_url, data=bad_words_data)
    # Проверяем, есть ли в ответе ошибка формы.
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    # Дополнительно убедимся, что комментарий не был создан.
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(self):
    comments_count = Comment.objects.count()
    # В начале теста в БД всегда есть 1 комментарий, созданный в setUpTestData.
    self.assertEqual(comments_count, 1)
    # От имени автора комментария отправляем DELETE-запрос на удаление.
    response = self.author_client.delete(self.delete_url)
    # Проверяем, что редирект привёл к разделу с комментариями.
    # Заодно проверим статус-коды ответов.
    self.assertRedirects(response, self.url_to_comments)
    # Считаем количество комментариев в системе.
    comments_count = Comment.objects.count()
    # Ожидаем ноль комментариев в системе.
    self.assertEqual(comments_count, 0)


def test_user_cant_delete_comment_of_another_user(self):
    comments_count = Comment.objects.count()
    # В начале теста в БД всегда есть 1 комментарий, созданный в setUpTestData.
    self.assertEqual(comments_count, 1)
    # Выполняем запрос на удаление от пользователя-читателя.
    response = self.reader_client.delete(self.delete_url)
    # Проверяем, что вернулась 404 ошибка.
    self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
    # Убедимся, что комментарий по-прежнему на месте.
    comments_count = Comment.objects.count()
    self.assertEqual(comments_count, 1)


def test_author_can_edit_comment(self):
    # Выполняем запрос на редактирование от имени автора комментария.
    response = self.author_client.post(self.edit_url, data=self.form_data)
    # Проверяем, что сработал редирект.
    self.assertRedirects(response, self.url_to_comments)
    # Обновляем объект комментария.
    self.comment.refresh_from_db()
    # Проверяем, что текст комментария соответствует обновленному.
    self.assertEqual(self.comment.text, self.NEW_COMMENT_TEXT)


def test_user_cant_edit_comment_of_another_user(self):
    # Выполняем запрос на редактирование от имени другого пользователя.
    response = self.reader_client.post(self.edit_url, data=self.form_data)
    # Проверяем, что вернулась 404 ошибка.
    self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
    # Обновляем объект комментария.
    self.comment.refresh_from_db()
    # Проверяем, что текст остался тем же, что и был.
    self.assertEqual(self.comment.text, self.COMMENT_TEXT)