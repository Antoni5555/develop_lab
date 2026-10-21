"""API прогресса (DRF). Вызывает js/progress.js; доступ — только вошедшим.

POST /api/progress/solved/  {"exercise": "python/first-steps/strings/sku-parts"}
POST /api/progress/import/  {"solved": [ключи задач], "viewed": [ключи уроков]}
"""
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import progress


def key_field():
    """Ключ урока или задачи: 3–4 slug через «/». Новый объект на каждое поле —
    DRF привязывает поле к одному сериализатору."""
    return serializers.RegexField(r'^[a-z0-9-]+(/[a-z0-9-]+){2,3}$', max_length=400)


class SolvedSerializer(serializers.Serializer):
    exercise = key_field()


class ImportSerializer(serializers.Serializer):
    solved = serializers.ListField(child=key_field(), max_length=2000, default=list)
    viewed = serializers.ListField(child=key_field(), max_length=2000, default=list)


class SolvedView(APIView):
    """Отметить задачу решённой."""

    def post(self, request):
        serializer = SolvedSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        exercise = progress.find_exercise(serializer.validated_data['exercise'])
        if exercise is None:
            return Response(
                {'detail': 'Задача не найдена'}, status=status.HTTP_404_NOT_FOUND,
            )
        progress.mark_solved(request.user, exercise)
        return Response({'solved': True})


class ImportView(APIView):
    """Перенести прогресс гостя из localStorage после входа."""

    def post(self, request):
        serializer = ImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        solved, viewed = progress.import_guest(
            request.user,
            serializer.validated_data['solved'],
            serializer.validated_data['viewed'],
        )
        return Response({'solved': solved, 'viewed': viewed})
