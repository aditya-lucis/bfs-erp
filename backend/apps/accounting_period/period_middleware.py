import json
import logging

from django.conf import settings
from django.http import JsonResponse

from .period_checker import PeriodChecker

logger = logging.getLogger(__name__)

# ── Default config ─────────────────────────────────────────────────────────────

DEFAULT_CONFIG = {
    'PROTECTED_PREFIXES': [
        '/api/v1/gl/',
        '/api/v1/ar/',
        '/api/v1/ap/',
        '/api/v1/purchases/',
    ],
    'EXCLUDED_PREFIXES': [
        '/api/v1/accounting/periods/',
        '/api/v1/auth/',
        '/api/v1/settings/',
    ],
    'DATE_FIELDS': [
        'transaction_date', 'journal_date', 'invoice_date',
        'posting_date', 'document_date', 'order_date',
        'delivery_date', 'payment_date', 'receipt_date',
        'issue_date', 'entry_date', 'date',
    ],
    'CHECK_LEVELS': ['ANNUAL', 'QUARTER', 'MONTHLY', 'ACCOUNTING'],
    'METHODS':      ['POST', 'PUT', 'PATCH', 'DELETE'],
    'STRICT_MODE':  False,
    'LOG_BLOCKED':  True,
}


class PeriodValidationMiddleware:
    """
    Django middleware that intercepts mutating HTTP requests and validates
    the transaction date against the Financial Period status.

    Flow:
        1. Check if method is in METHODS (POST/PUT/PATCH/DELETE)
        2. Check if URL is in PROTECTED_PREFIXES
        3. Check if URL is NOT in EXCLUDED_PREFIXES
        4. Parse JSON body, find first DATE_FIELD that exists
        5. Run PeriodChecker.check() on that date
        6. If closed → return HTTP 403 JSON immediately (request never reaches view)
        7. If open → pass through to view normally
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self._config      = {**DEFAULT_CONFIG, **getattr(settings, 'PERIOD_CHECK_CONFIG', {})}

    def __call__(self, request):
        # Only run on configured methods
        if request.method not in self._config['METHODS']:
            return self.get_response(request)

        path = request.path

        # Check exclusions first
        for excluded in self._config['EXCLUDED_PREFIXES']:
            if path.startswith(excluded):
                return self.get_response(request)

        # Check if path is protected
        is_protected = any(
            path.startswith(prefix)
            for prefix in self._config['PROTECTED_PREFIXES']
        )
        if not is_protected:
            return self.get_response(request)

        # Skip DELETE — usually no date in body
        if request.method == 'DELETE':
            return self.get_response(request)

        # Parse body
        txn_date = self._extract_date_from_body(request)
        if not txn_date:
            # No date field found — skip period check
            return self.get_response(request)

        # Run period check
        result = PeriodChecker.check(
            txn_date,
            company=self._resolve_company(request),
            levels=self._config['CHECK_LEVELS'],
            raise_exception=False,
        )

        if result.is_closed:
            if self._config['LOG_BLOCKED']:
                logger.warning(
                    '[PeriodMiddleware] BLOCKED | method=%s | path=%s | date=%s | level=%s | period=%s | user=%s',
                    request.method,
                    path,
                    txn_date,
                    result.level,
                    result.period_label,
                    getattr(request, 'user', 'anonymous'),
                )

            return JsonResponse(
                {
                    'detail':        result.message,
                    'period_closed': True,
                    'blocked_level': result.level,
                    'period_label':  result.period_label,
                    'checked_levels': result.checked_levels,
                },
                status=403,
            )

        return self.get_response(request)

    def _extract_date_from_body(self, request) -> str | None:
        """
        Parse JSON body and return the first date field value found.
        Caches parsed body in request._period_body to avoid double-parse.
        """
        if not request.content_type or 'json' not in request.content_type.lower():
            return None

        # Cache parsed body
        if not hasattr(request, '_period_body'):
            try:
                request._period_body = json.loads(request.body or '{}')
            except (json.JSONDecodeError, Exception):
                request._period_body = {}

        body = request._period_body
        if not isinstance(body, dict):
            return None

        for field in self._config['DATE_FIELDS']:
            val = body.get(field)
            if val:
                return val
        return None

    def _resolve_company(self, request):
        """Resolve company from request. Override if multi-company needed."""
        try:
            from apps.organization.models import Company
            return Company.get_default()
        except Exception:
            return None