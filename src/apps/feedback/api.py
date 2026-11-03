"""API сообщений об ошибках (DRF). Вызывает js/report-error.js; только вошедшим.

POST /api/reports/  {"source": "python/first-steps/strings[/sku-parts]",
                     "quote": …, "context": …, "comment": …}
Не больше 20 сообщений в час на пользователя (REST_FRAMEWORK → 'reports').
"""
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .services import reports


class ReportSerializer(serializers.Serializer):
    source = serializers.RegexField(r'^[a-z0-9-]+(/[a-z0-9-]+){2,3}$', max_length=400)
    quote = serializers.CharField(max_length=reports.MAX_QUOTE)
    context = serializers.CharField(max_length=reports.MAX_CONTEXT, allow_blank=True,
                                    required=False, default='')
    comment = serializers.CharField(max_length=reports.MAX_COMMENT, allow_blank=True,
                                    required=False, default='')


class ReportListView(APIView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'reports'

    def post(self, request):
        serializer = ReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        report = reports.create_report(request.user, data['source'], data['quote'],
                                       data['context'], data['comment'])
        if report is None:
            return Response({'detail': 'Не найдено, к чему относится сообщение'},
                            status=status.HTTP_404_NOT_FOUND)
        return Response({'id': report.pk}, status=status.HTTP_201_CREATED)
