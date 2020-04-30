from django.contrib import admin
from .models import Person


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("source_id", "name", "gender", "popularity", "display_films")
    search_fields = ("id", "source_id", "name", "gender", "popularity", "profile_path", "adult")
