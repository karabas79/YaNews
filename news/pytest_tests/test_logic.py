from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, detail_url, form_data):
    url = detail_url
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_authorized_user_can_create_comment(
    author_client,
    author,
    detail_url,
    form_data,
    news
):
    url = detail_url
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    assert response.url == f'{url}#comments'
    new_comment = Comment.objects.get()

    assert new_comment.text == form_data['text']
    assert new_comment.news == news
    assert new_comment.author == author


def test_user_cant_use_bad_words(author_client, detail_url, form_data):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(detail_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(author_client, delete_url, url_to_comments):
    comments_count = Comment.objects.count()
    assert comments_count == 1
    response = author_client.delete(delete_url)
    # pdb.set_trace()
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(
    delete_url,
    not_author_client
):
    comments_count = Comment.objects.count()
    assert comments_count == 1
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(
    author_client,
    comment,
    edit_url,
    form_data,
    url_to_comments
):
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(
    comment,
    edit_url,
    form_data,
    not_author_client
):
    original_text = comment.text
    response = not_author_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == original_text
