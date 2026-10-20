"""Общие фикстуры pytest."""
import shutil
from pathlib import Path

import pytest

from apps.courses.services.content_loader import ContentLoader


FIXTURE_CONTENT = Path(__file__).parent / 'fixtures' / 'content'


@pytest.fixture
def content_dir(tmp_path):
    """Копия тестового контента во временной папке — тест может её менять."""
    target = tmp_path / 'content'
    shutil.copytree(FIXTURE_CONTENT, target)
    return target


@pytest.fixture
def loaded_content(db, content_dir):
    """Тестовый контент, загруженный в БД. Возвращает папку контента."""
    ContentLoader(content_dir).load()
    return content_dir
