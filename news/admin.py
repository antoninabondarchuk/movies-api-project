from django.contrib import admin
from news.models import NewsPost


@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'publish_date', 'display_films', 'display_tvs', )
    search_fields = ('title', 'display_films', 'display_tvs', )
