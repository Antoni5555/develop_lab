"""Фабрики тестовых данных (factory-boy): создают записи с разумными значениями."""
import factory

from apps.courses.models import Course, Exercise, Lesson, Section, Topic, Track


class TrackFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Track

    slug = factory.Sequence(lambda n: f'track-{n}')
    title = factory.Sequence(lambda n: f'Направление {n}')


class CourseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Course

    track = factory.SubFactory(TrackFactory)
    slug = factory.Sequence(lambda n: f'course-{n}')
    title = factory.Sequence(lambda n: f'Курс {n}')
    engine = Course.Engine.PYTHON
    order = factory.Sequence(lambda n: n * 10)


class SectionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Section

    course = factory.SubFactory(CourseFactory)
    slug = factory.Sequence(lambda n: f'section-{n}')
    title = factory.Sequence(lambda n: f'Раздел {n}')
    order = factory.Sequence(lambda n: n)


class TopicFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Topic

    section = factory.SubFactory(SectionFactory)
    slug = factory.Sequence(lambda n: f'topic-{n}')
    title = factory.Sequence(lambda n: f'Тема {n}')
    order = factory.Sequence(lambda n: n)


class LessonFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Lesson

    topic = factory.SubFactory(TopicFactory)
    title = factory.LazyAttribute(lambda lesson: lesson.topic.title)
    body_html = '<h2>Теория</h2><p>Текст.</p>'


class ExerciseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Exercise

    topic = factory.SubFactory(TopicFactory)
    slug = factory.Sequence(lambda n: f'exercise-{n}')
    title = factory.Sequence(lambda n: f'Задача {n}')
    type = Exercise.Type.PREDICT
    pitfall = 'Подводный камень.'
    statement_html = '<p>Что выведет код?</p>'
    explanation_html = '<p>Разбор.</p>'
    spec = factory.LazyFunction(lambda: {'code': 'print(1)', 'answer': '1\n'})


def topic_with_lesson(section, **kwargs):
    """Тема с уроком и двумя задачами — как в настоящем контенте."""
    topic = TopicFactory(section=section, **kwargs)
    LessonFactory(topic=topic)
    ExerciseFactory.create_batch(2, topic=topic)
    return topic


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'accounts.User'
        skip_postgeneration_save = True

    email = factory.Sequence(lambda n: f'user{n}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'secret-pass-123')

    @factory.post_generation
    def save_password(obj, create, extracted, **kwargs):
        if create:
            obj.save()
