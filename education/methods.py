"""Вынесенные функции для работы сайта."""

from django.db.models import OuterRef, Count, Exists

from authentication.models import User
from education.models import Stars, Courses


def get_metadata(md_content):
    """Извлекает метаданные из файла."""
    metadata = {}
    metadata_start = md_content.find("[metadata]")
    metadata_end = md_content.find("[/metadata]")

    if metadata_start != -1 and metadata_end != -1:
        metadata_lines =\
            md_content[metadata_start + len("[metadata]"):metadata_end].strip().splitlines()
        for line in metadata_lines:
            if line.strip():
                key, value = line.split(": ", 1)
                metadata[key.strip()] = value.strip()

        md_content = md_content[metadata_end + len("[/metadata]"):].strip()

    return metadata, md_content


def get_most_popular_courses(user: User):
    """Используется для получения 3х самых популярных курсов."""
    if user.is_authenticated:
        subquery = Stars.objects.filter(
            course=OuterRef('pk'),
            user=user
        )
        popular_courses = Courses.objects.prefetch_related('topics').annotate(
            stars_count=Count('stars'),
            is_stared=Exists(subquery)
        ).order_by('-stars_count')[:3]
    else:
        popular_courses = Courses.objects.prefetch_related('topics').annotate(
            stars_count=Count('stars')
        ).order_by('-stars_count')[:3]
    return popular_courses
