"""Хранилище статики для production."""
from django.contrib.staticfiles.storage import ManifestStaticFilesStorage


class StaticStorage(ManifestStaticFilesStorage):
    """Как ManifestStaticFilesStorage, но переписывает и import между JS-модулями.

    collectstatic добавляет к файлам хеш (editor.js → editor.3f9a1c.js), чтобы
    браузер кэшировал их надолго. Без этой опции `import './editor.js'` грузил бы
    файл без хеша — после обновления сайта браузер мог бы взять старую версию.
    """

    support_js_module_import_aggregation = True
