import pytest
from datetime import datetime, timedelta

from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import News, Comment
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )
    return news


@pytest.fixture
def id_for_news(news):
    return (news.id,)


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )
    return comment


@pytest.fixture
def form_data():
    return {
        'title': 'Новый заголовок',
        'text': 'Новый текст',
        'slug': 'new-slug'
    }


@pytest.fixture
def news_in_page():
    today = datetime.today()
    news_list = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(NEWS_COUNT_ON_HOME_PAGE)
    ]
    News.objects.bulk_create(news_list)
    return news_list


@pytest.fixture
def comment_in_page(author, news):
    # today = datetime.today()
    now = datetime.now()
    comment_list = []
    for index in range(10):
        # Создаём объект и записываем его в переменную.
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст комментария {index}',
        )
        # Сразу после создания меняем время создания комментария.
        now = timezone.now()
        comment.created = now + timedelta(days=index)
        comment.save()
        comment_list.append(comment)
    return comment_list


@pytest.fixture
def detail_url(news):
    """Создает URL для страницы детали новости."""
    return reverse('news:detail', args=[news.id])


@pytest.fixture
def edit_url(comment):
    """Создает URL для страницы детали новости."""
    return reverse('news:edit', args=[comment.id])


@pytest.fixture
def delete_url(comment):
    """Создает URL для страницы детали новости."""
    return reverse('news:delete', args=[comment.id])


@pytest.fixture
def url_to_comments(detail_url):
    return detail_url + '#comments'
