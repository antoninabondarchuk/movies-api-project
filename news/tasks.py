from django.core.mail import send_mail
from myproject.celery import app
from users.models import UserAccount
from .models import NewsPost


@app.task
def send_emails_news(yesterday):
    yesterday_news = NewsPost.objects.filter(publish_date=yesterday)
    for new_post in yesterday_news:
        film_ids = [film.id for film in new_post.film.all()]
        tv_ids = [tv.id for tv in new_post.tv.all()]
        user_accounts = UserAccount.objects.filter(wish_list__id__in=film_ids)\
            .union(UserAccount.objects.filter(wish_list_tv__id__in=tv_ids))
        emails_to_send = [user_account.user.email for user_account in user_accounts]
        send_mail(new_post.title, new_post.overview,
                  'films.api@gmail.com', emails_to_send, fail_silently=False)
