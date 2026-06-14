from django.db import models as dj_models
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.organization.models import Company
from apps.rbac.permissions import HasFunctionPermission

from .models import ApprovalMatrix, ApprovalRequest, DocumentSignature
from .constants import ApprovalStatus, StepStatus
from .serializers import (
    ApprovalMatrixListSerializer,
    ApprovalMatrixDetailSerializer,
    ApprovalMatrixWriteSerializer,
    ApprovalResolveSerializer,
    ApprovalRequestSerializer,
    ApprovalRequestStepSerializer,
    DocumentSignatureSerializer,
    ApprovalActionSerializer,
    ApprovalRequestSubmitSerializer,
)
from .services import (
    get_document_types, get_approval_roles, get_matrix_queryset,
    create_approval_request, approve_step, reject_request,
    get_document_signatures, ApprovalMatrixError
)


RBAC_CODE = 'SETTINGS-REQUEST-APPROVAL-SETTING'


class DocumentTypeListView(APIView):
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = RBAC_CODE

    def get(self, request):
        return Response(get_document_types())


class ApprovalRoleListView(APIView):
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = RBAC_CODE

    def get(self, request):
        return Response(get_approval_roles())


class ApprovalMatrixListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = RBAC_CODE

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ApprovalMatrixWriteSerializer
        return ApprovalMatrixListSerializer

    def get_queryset(self):
        qs = get_matrix_queryset(Company.get_default())
        document_code = self.request.query_params.get('document_code')
        creator_position = self.request.query_params.get('creator_position')
        if document_code:
            qs = qs.filter(document_code=document_code)
        if creator_position:
            qs = qs.filter(creator_position_id=creator_position)
        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        matrix = serializer.save()
        detail = ApprovalMatrixDetailSerializer(
            get_matrix_queryset().get(pk=matrix.pk),
        )
        return Response(detail.data, status=status.HTTP_201_CREATED)


class ApprovalMatrixDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = RBAC_CODE

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return ApprovalMatrixWriteSerializer
        return ApprovalMatrixDetailSerializer

    def get_queryset(self):
        return get_matrix_queryset(Company.get_default())

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ApprovalMatrixWriteSerializer(
            data={
                **request.data,
                'document_code': request.data.get('document_code', instance.document_code),
                'creator_position': request.data.get(
                    'creator_position', instance.creator_position_id,
                ),
            },
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        matrix = serializer.save()
        detail = ApprovalMatrixDetailSerializer(
            get_matrix_queryset().get(pk=matrix.pk),
        )
        return Response(detail.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save(update_fields=['is_active', 'updated_at'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class ApprovalResolveView(APIView):
    """
    Library endpoint — resolve approval steps for a document value.
    Can be called from RAP, PR, PO modules in the future.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ApprovalResolveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.resolve()
        return Response(result)


class ApprovalMatrixLookupView(APIView):
    """GET matrix by document_code + creator_position (for settings form load)."""
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = RBAC_CODE

    def get(self, request):
        document_code = request.query_params.get('document_code')
        creator_position = request.query_params.get('creator_position')
        if not document_code or not creator_position:
            return Response(
                {'detail': 'document_code dan creator_position wajib diisi.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        matrix = get_matrix_queryset().filter(
            document_code=document_code,
            creator_position_id=creator_position,
        ).first()
        if not matrix:
            return Response(None)
        return Response(ApprovalMatrixDetailSerializer(matrix).data)


class ApprovalRequestListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ApprovalRequestSubmitSerializer
        return ApprovalRequestSerializer

    def get_queryset(self):
        user = self.request.user
        qs = ApprovalRequest.objects.all().select_related(
            'company', 'creator__employee_profile', 'creator_position__department'
        ).prefetch_related(
            'steps__position__department', 'steps__approved_by__employee_profile'
        )

        inbox = self.request.query_params.get('inbox')
        if inbox == 'true':
            employee = getattr(user, 'employee_profile', None)
            if not employee:
                return ApprovalRequest.objects.none()
            
            # Show only PENDING request step matching my position where it's my turn
            qs = qs.filter(
                status=ApprovalStatus.PENDING,
                steps__step_number=dj_models.F('current_step_number'),
                steps__position_id=employee.position_id,
                steps__status=StepStatus.PENDING
            )

        document_code = self.request.query_params.get('document_code')
        status_filter = self.request.query_params.get('status')
        document_number = self.request.query_params.get('document_number')

        if document_code:
            qs = qs.filter(document_code=document_code)
        if status_filter:
            qs = qs.filter(status=status_filter)
        if document_number:
            qs = qs.filter(document_number__icontains=document_number)

        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            req = create_approval_request(
                document_code=serializer.validated_data['document_code'],
                document_id=serializer.validated_data['document_id'],
                document_number=serializer.validated_data['document_number'],
                creator_user=request.user,
                amount=serializer.validated_data.get('amount'),
                quantity=serializer.validated_data.get('quantity'),
            )
            detail = ApprovalRequestSerializer(req, context={'request': request})
            return Response(detail.data, status=status.HTTP_201_CREATED)
        except ApprovalMatrixError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class ApprovalRequestDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ApprovalRequestSerializer
    queryset = ApprovalRequest.objects.all().select_related(
        'company', 'creator__employee_profile', 'creator_position__department'
    ).prefetch_related(
        'steps__position__department', 'steps__approved_by__employee_profile'
    )


class ApprovalRequestApproveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        serializer = ApprovalActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get client IP & User Agent
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        try:
            req = approve_step(
                approval_request_id=pk,
                user=request.user,
                remarks=serializer.validated_data.get('remarks'),
                ip_address=ip,
                user_agent=user_agent,
            )
            detail = ApprovalRequestSerializer(req, context={'request': request})
            return Response(detail.data)
        except ApprovalMatrixError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class ApprovalRequestRejectView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        serializer = ApprovalActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Remarks are mandatory for rejection
        remarks = serializer.validated_data.get('remarks', '').strip()
        if not remarks:
            return Response(
                {'detail': 'Alasan penolakan (remarks) wajib diisi.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get client IP & User Agent
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        try:
            req = reject_request(
                approval_request_id=pk,
                user=request.user,
                remarks=remarks,
                ip_address=ip,
                user_agent=user_agent,
            )
            detail = ApprovalRequestSerializer(req, context={'request': request})
            return Response(detail.data)
        except ApprovalMatrixError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class DocumentSignatureListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        doc_code = request.query_params.get('document_code')
        doc_id = request.query_params.get('document_id')
        if not doc_code or not doc_id:
            return Response(
                {'detail': 'document_code dan document_id wajib diisi.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        sigs = get_document_signatures(doc_code, doc_id)
        serializer = DocumentSignatureSerializer(sigs, many=True)
        return Response(serializer.data)

