"""
BFS ERP — Period Status API
apps/accounting/views_period_status.py

Exposes period check results to the frontend so Vue components
can validate dates in real-time before submitting forms.

Endpoints:
    GET  /api/v1/accounting/periods/status/?date=2026-06-15
    POST /api/v1/accounting/periods/status/bulk/    (check multiple dates at once)
"""

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .period_checker import PeriodChecker


class PeriodStatusView(APIView):
    """
    GET /api/v1/accounting/periods/status/?date=YYYY-MM-DD
    GET /api/v1/accounting/periods/status/?date=YYYY-MM-DD&levels=MONTHLY,ACCOUNTING

    Returns the period status for a given date.
    Used by frontend to show real-time period open/closed indicators in forms.

    Response (open):
        {
            "date": "2026-06-15",
            "is_open": true,
            "message": "Period June 2026 is open for transactions.",
            "checked_levels": ["ANNUAL", "QUARTER", "MONTHLY", "ACCOUNTING"],
            "details": {
                "ANNUAL":     { "is_open": true, "period_label": "2026", "status": "OPEN" },
                "QUARTER":    { "is_open": true, "period_label": "2026 Q2", "status": "OPEN" },
                "MONTHLY":    { "is_open": true, "period_label": "June 2026", "status": "OPEN" },
                "ACCOUNTING": { "is_open": true, "period_label": "June 2026", "status": "OPEN" }
            }
        }

    Response (closed):
        {
            "date": "2025-03-10",
            "is_open": false,
            "blocked_level": "MONTHLY",
            "period_label": "March 2025",
            "message": "... period closed ...",
            "checked_levels": ["ANNUAL", "QUARTER", "MONTHLY"],
            "details": { ... }
        }
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        date_str = request.query_params.get('date')
        if not date_str:
            return Response(
                {'detail': 'Query param "date" is required. Format: YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        levels_param = request.query_params.get('levels')
        levels = [l.strip().upper() for l in levels_param.split(',')] if levels_param else None

        result = PeriodChecker.check(
            date_str,
            levels=levels,
            raise_exception=False,
        )

        response_data = {
            'date':           date_str,
            'is_open':        result.is_open,
            'message':        result.message,
            'checked_levels': result.checked_levels,
            'details':        result.details,
        }

        if result.is_closed:
            response_data['blocked_level'] = result.level
            response_data['period_label']  = result.period_label

        return Response(response_data)


class PeriodStatusBulkView(APIView):
    """
    POST /api/v1/accounting/periods/status/bulk/

    Check multiple dates at once. Useful for bulk-import validation.

    Request:
        { "dates": ["2026-06-15", "2026-07-01", "2025-12-31"] }

    Response:
        {
            "results": [
                { "date": "2026-06-15", "is_open": true, ... },
                { "date": "2026-07-01", "is_open": true, ... },
                { "date": "2025-12-31", "is_open": false, "blocked_level": "ANNUAL", ... }
            ],
            "all_open": false,
            "blocked_count": 1
        }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        dates = request.data.get('dates', [])
        levels_param = request.data.get('levels')
        if levels_param:
            if isinstance(levels_param, str):
                levels = [l.strip().upper() for l in levels_param.split(',')]
            else:
                levels = [str(l).strip().upper() for l in levels_param]
        else:
            levels = None

        if not dates or not isinstance(dates, list):
            return Response(
                {'detail': '"dates" must be a non-empty list of date strings.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(dates) > 100:
            return Response(
                {'detail': 'Maximum 100 dates per bulk request.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        results      = []
        blocked_count = 0

        for date_str in dates:
            result = PeriodChecker.check(
                date_str,
                levels=levels,
                raise_exception=False,
            )
            row = {
                'date':           date_str,
                'is_open':        result.is_open,
                'message':        result.message,
                'checked_levels': result.checked_levels,
            }
            if result.is_closed:
                row['blocked_level'] = result.level
                row['period_label']  = result.period_label
                blocked_count += 1

            results.append(row)

        return Response({
            'results':       results,
            'all_open':      blocked_count == 0,
            'blocked_count': blocked_count,
            'total':         len(dates),
        })