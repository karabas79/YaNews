import pytest

from django.urls import reverse

from yanews.settings import NEWS_COUNT_ON_HOME_PAGE
from news.forms import CommentForm


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, news_on_page',
    (
        (pytest.lazy_fixture('not_author_client'), NEWS_COUNT_ON_HOME_PAGE),
    )
)
def test_news_count_and_news_order(
    news,
    news_in_page,
    parametrized_client,
    news_on_page
):
    url = reverse('news:home')
    response = parametrized_client.get(url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == news_on_page
    dates = [news.date for news in object_list]
    sorted_dates = sorted(dates, reverse=True)
    assert dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(comment_in_page, news, author_client):
    url = reverse('news:detail', args=[news.id])
    response = author_client.get(url)
    assert 'news' in response.context
    news_obj = response.context['news']
    all_comments = news_obj.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_comments = sorted(all_timestamps)
    assert all_timestamps == sorted_comments


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, detail_url):
    response = client.get(detail_url)
    assert 'form' not in response.context

@pytest.mark.django_db
def test_authorized_client_has_form(not_author_client, detail_url):
    response = not_author_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
