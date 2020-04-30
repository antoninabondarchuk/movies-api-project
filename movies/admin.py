from django.contrib import admin
from django.forms import BaseInlineFormSet
from comments.models import Comment
from news.models import NewsPost
from .models import Film, Genre, Tv, TvGenre
from django.utils.translation import gettext_lazy as _
from django.db.models import Max, Min

STEP = 10


class DateFilter(admin.SimpleListFilter):
    empty_params = {'parameter_name': ''}
    none_params = {'parameter_name': None}
    parameter_name = None

    def filter_date(self, decade):
        pass

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        self.buffer_queryset = qs
        min_year = int(qs.exclude(**self.empty_params)
                       .aggregate(Min(f'{self.parameter_name}'))[f'{self.parameter_name}__min'][:4])
        start_decade = int(min_year / 10) * 10
        max_year = int(qs.aggregate(Max(f'{self.parameter_name}'))[f'{self.parameter_name}__max'][:4])

        for decade in range(start_decade, max_year + 1, STEP):
            if self.filter_date(decade).exists():
                yield (f'{decade}s', _(f'{decade}s'))
        if qs.filter(**self.empty_params).union(qs.filter(**self.none_params)):
            yield ('unknown', _('unknown'))

    def queryset(self, request, queryset):
        self.buffer_queryset = queryset
        min_year = int(queryset.exclude(**self.empty_params)
                       .aggregate(Min(f'{self.parameter_name}'))[f'{self.parameter_name}__min'][:4])
        start_decade = int(min_year / 10) * 10
        max_year = int(queryset.aggregate(Max(f'{self.parameter_name}'))[f'{self.parameter_name}__max'][:4])

        for decade in range(start_decade, max_year + 1, STEP):
            if self.value() == f'{decade}s':
                return self.filter_date(decade)
        if self.value() == 'unknown':
            return queryset.filter(**self.empty_params).union(queryset.filter(**self.none_params))
        return None


class ReleaseDateFilter(DateFilter):
    title = _('Release date')
    parameter_name = 'release_date'
    empty_params = {'release_date': ''}
    none_params = {'release_date': None}

    def filter_date(self, decade):
        return self.buffer_queryset.filter(release_date__gte=f"{decade}-01-01",
                                           release_date__lte=f"{decade + STEP}-01-01")


class FirstAirDateFilter(DateFilter):
    title = _('First air date')
    parameter_name = 'first_air_date'
    empty_params = {'first_air_date': ''}
    none_params = {'first_air_date': None}

    def filter_date(self, decade):
        return self.buffer_queryset.filter(first_air_date__gte=f"{decade}-01-01",
                                           first_air_date__lte=f"{decade + STEP}-01-01")


class NewsFilmLimitFormSet(BaseInlineFormSet):
    def get_queryset(self):
        qs = super(NewsFilmLimitFormSet, self).get_queryset()
        return qs[:10]


class NewsFilmInlineAdmin(admin.StackedInline):
    model = NewsPost.film.through
    extra = 1
    formset = NewsFilmLimitFormSet


class NewsTvLimitFormSet(BaseInlineFormSet):
    def get_queryset(self):
        qs = super(NewsTvLimitFormSet, self).get_queryset()
        return qs[:10]


class NewsTvInlineAdmin(admin.StackedInline):
    model = NewsPost.tv.through
    extra = 1
    formset = NewsTvLimitFormSet


class CommentsLimitFormSet(BaseInlineFormSet):
    def get_queryset(self):
        qs = super(CommentsLimitFormSet, self).get_queryset()
        return qs[:10]


class CommentsInlineAdmin(admin.StackedInline):
    model = Comment
    extra = 1
    formset = CommentsLimitFormSet


@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    list_display = ("source_id", "title", "original_language", "original_title",
                    "popularity", "release_date", 'display_genres', )
    search_fields = ("id", "source_id", "popularity", "vote_average",
                     "vote_count", "poster_path", "backdrop_path",
                     "original_language", "type", "overview", "title",
                     "original_title", "release_date", )
    list_filter = ("genre_ids", ReleaseDateFilter, )
    inlines = [CommentsInlineAdmin, NewsFilmInlineAdmin, ]


@admin.register(Tv)
class TvAdmin(admin.ModelAdmin):
    list_display = ("source_id", "name", "original_language", "original_name",
                    "popularity", "first_air_date", 'display_genres')
    search_fields = ("id", "source_id", "popularity", "vote_average",
                     "vote_count", "poster_path", "backdrop_path",
                     "original_language", "type", "overview", "name",
                     "original_name", "first_air_date",)
    list_filter = ("genre_ids", FirstAirDateFilter,)
    inlines = [NewsTvInlineAdmin, CommentsInlineAdmin, ]


@admin.register(TvGenre, Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("source_id", "title")
    search_fields = ("id", "source_id", "title")
