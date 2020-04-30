from myproject.celery import app
from .models import Person
from movies.models import Film, Tv
from movies.tasks import get_paginated_list
import logging

logger = logging.getLogger()


@app.task
def get_paginated_people(url):
    pages_results = get_paginated_list(url)

    for person_dict in pages_results:
        person, _ = Person.objects.get_or_create(source_id=person_dict.get('id'))
        person.popularity = person_dict.get('popularity')
        person.gender = person_dict.get('gender')
        person.profile_path = person_dict.get('profile_path')
        person.adult = person_dict.get('adult')
        person.name = person_dict.get('name')
        person.save()

        for film_dict in person_dict['known_for']:
            try:
                if film_dict['media_type'] == 'movie':
                    film = Film.objects.get(source_id=film_dict.get('id'))
                    person.known_for.add(film)
                else:
                    tv = Tv.objects.get(source_id=film_dict.get('id'))
                    person.known_for_tv.add(tv)
            except Film.DoesNotExist:
                logger.exception("Such film does not exist!")
            except Tv.DoesNotExist:
                logger.exception("Such film does not exist!")
