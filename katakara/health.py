from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import connection
from django.db.utils import OperationalError

class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        db_status = "ok"

        try:
            connection.ensure_connection()
        except OperationalError:
            db_status = "unreachable"

        status_code = 200 if db_status == "ok" else 503

        return Response(
            {
                "status": "ok" if db_status == "ok" else "degraded",
                "service": "katakara",
                "database": db_status,
            },
            status=status_code
        )
