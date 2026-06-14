from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from apps.organization.models import Company
from .constants import DocumentType, ApprovalBasis, ApprovalRole, ApprovalStatus, StepStatus
from .models import (
    ApprovalMatrix, ApprovalMatrixRange, ApprovalMatrixStep,
    ApprovalRequest, ApprovalRequestStep, DocumentSignature
)
from .services import validate_ranges, ApprovalMatrixError


class ApprovalMatrixStepSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    position_name = serializers.CharField(source='position.name', read_only=True)
    position_code = serializers.CharField(source='position.code', read_only=True)
    department_name = serializers.CharField(
        source='position.department.name', read_only=True,
    )

    class Meta:
        model = ApprovalMatrixStep
        fields = [
            'id', 'step_number', 'role', 'role_display',
            'position', 'position_name', 'position_code', 'department_name',
        ]


class ApprovalMatrixStepWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalMatrixStep
        fields = ['step_number', 'role', 'position']

    def validate_role(self, value):
        if value not in ApprovalRole.values:
            raise serializers.ValidationError('Role tidak valid.')
        return value


class ApprovalMatrixRangeSerializer(serializers.ModelSerializer):
    steps = ApprovalMatrixStepSerializer(many=True, read_only=True)
    step_count = serializers.SerializerMethodField()

    class Meta:
        model = ApprovalMatrixRange
        fields = [
            'id', 'from_value', 'to_value', 'order_no',
            'step_count', 'steps',
        ]

    def get_step_count(self, obj):
        return obj.steps.count()


class ApprovalMatrixRangeWriteSerializer(serializers.Serializer):
    from_value = serializers.DecimalField(max_digits=18, decimal_places=2)
    to_value = serializers.DecimalField(max_digits=18, decimal_places=2)
    order_no = serializers.IntegerField(required=False, default=0)
    steps = ApprovalMatrixStepWriteSerializer(many=True)

    def validate_steps(self, value):
        if not value:
            raise serializers.ValidationError('Minimal satu step approval.')
        numbers = [s['step_number'] for s in value]
        if len(numbers) != len(set(numbers)):
            raise serializers.ValidationError('Step number tidak boleh duplikat.')
        return value


class ApprovalMatrixListSerializer(serializers.ModelSerializer):
    document_name = serializers.CharField(read_only=True)
    creator_position_name = serializers.CharField(
        source='creator_position.name', read_only=True,
    )
    creator_department_name = serializers.CharField(
        source='creator_position.department.name', read_only=True,
    )
    basis_display = serializers.CharField(source='get_basis_display', read_only=True)
    range_count = serializers.SerializerMethodField()

    class Meta:
        model = ApprovalMatrix
        fields = [
            'id', 'document_code', 'document_name',
            'creator_position', 'creator_position_name', 'creator_department_name',
            'basis', 'basis_display', 'is_active',
            'range_count', 'created_at', 'updated_at',
        ]

    def get_range_count(self, obj):
        return obj.ranges.count()


class ApprovalMatrixDetailSerializer(serializers.ModelSerializer):
    document_name = serializers.CharField(read_only=True)
    creator_position_name = serializers.CharField(
        source='creator_position.name', read_only=True,
    )
    creator_department_name = serializers.CharField(
        source='creator_position.department.name', read_only=True,
    )
    basis_display = serializers.CharField(source='get_basis_display', read_only=True)
    ranges = ApprovalMatrixRangeSerializer(many=True, read_only=True)

    class Meta:
        model = ApprovalMatrix
        fields = [
            'id', 'document_code', 'document_name',
            'creator_position', 'creator_position_name', 'creator_department_name',
            'basis', 'basis_display', 'is_active',
            'ranges', 'created_at', 'updated_at',
        ]


class ApprovalMatrixWriteSerializer(serializers.Serializer):
    document_code = serializers.ChoiceField(choices=DocumentType.choices)
    creator_position = serializers.IntegerField()
    basis = serializers.ChoiceField(choices=ApprovalBasis.choices, default=ApprovalBasis.AMOUNT)
    is_active = serializers.BooleanField(default=True)
    ranges = ApprovalMatrixRangeWriteSerializer(many=True)

    def validate_creator_position(self, value):
        from apps.organization.models import Position
        if not Position.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError('Posisi tidak ditemukan atau tidak aktif.')
        return value

    def validate(self, data):
        try:
            validate_ranges(data['ranges'], data.get('basis', ApprovalBasis.AMOUNT))
        except ApprovalMatrixError as exc:
            raise serializers.ValidationError({'ranges': str(exc)}) from exc
        return data

    @transaction.atomic
    def create(self, validated_data):
        company = Company.get_default()
        request = self.context.get('request')
        user = request.user if request else None

        ranges_data = validated_data.pop('ranges')

        matrix, _created = ApprovalMatrix.objects.update_or_create(
            company=company,
            document_code=validated_data['document_code'],
            creator_position_id=validated_data['creator_position'],
            defaults={
                'basis': validated_data['basis'],
                'is_active': validated_data['is_active'],
                'created_by': user,
            },
        )

        matrix.ranges.all().delete()

        for order, block in enumerate(ranges_data):
            range_obj = ApprovalMatrixRange.objects.create(
                matrix=matrix,
                from_value=block['from_value'],
                to_value=block['to_value'],
                order_no=block.get('order_no', order),
            )
            for step_data in block['steps']:
                ApprovalMatrixStep.objects.create(
                    range=range_obj,
                    step_number=step_data['step_number'],
                    role=step_data['role'],
                    position_id=step_data['position'],
                )

        return matrix


class ApprovalResolveSerializer(serializers.Serializer):
    document_code = serializers.ChoiceField(choices=DocumentType.choices)
    creator_position_id = serializers.IntegerField()
    amount = serializers.DecimalField(
        max_digits=18, decimal_places=2, required=False, allow_null=True,
    )
    quantity = serializers.DecimalField(
        max_digits=18, decimal_places=2, required=False, allow_null=True,
    )

    def validate(self, data):
        doc_code = data['document_code']
        # Will be validated at resolve time based on matrix basis
        return data

    def resolve(self):
        from .services import resolve_approval_steps, ApprovalMatrixError
        try:
            return resolve_approval_steps(
                document_code=self.validated_data['document_code'],
                creator_position_id=self.validated_data['creator_position_id'],
                amount=self.validated_data.get('amount'),
                quantity=self.validated_data.get('quantity'),
            )
        except ApprovalMatrixError as exc:
            raise serializers.ValidationError(str(exc)) from exc


class ApprovalRequestStepSerializer(serializers.ModelSerializer):
    position_name = serializers.CharField(source='position.name', read_only=True)
    position_code = serializers.CharField(source='position.code', read_only=True)
    department_name = serializers.CharField(source='position.department.name', default='', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.username', default='', read_only=True)
    approved_by_employee_name = serializers.CharField(source='approved_by.employee_profile.full_name', default='', read_only=True)

    class Meta:
        model = ApprovalRequestStep
        fields = [
            'id', 'step_number', 'role', 'role_display', 'position', 'position_name', 
            'position_code', 'department_name', 'status', 'status_display', 
            'approved_by', 'approved_by_name', 'approved_by_employee_name', 
            'approved_at', 'remarks'
        ]


class ApprovalRequestSerializer(serializers.ModelSerializer):
    document_name = serializers.SerializerMethodField()
    creator_name = serializers.CharField(source='creator.username', default='', read_only=True)
    creator_employee_name = serializers.CharField(source='creator.employee_profile.full_name', default='', read_only=True)
    creator_position_name = serializers.CharField(source='creator_position.name', read_only=True)
    creator_department_name = serializers.CharField(source='creator_position.department.name', default='', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    basis_display = serializers.CharField(source='get_basis_display', read_only=True)
    steps = ApprovalRequestStepSerializer(many=True, read_only=True)
    is_my_turn = serializers.SerializerMethodField()

    class Meta:
        model = ApprovalRequest
        fields = [
            'id', 'document_code', 'document_name', 'document_id', 'document_number',
            'creator', 'creator_name', 'creator_employee_name', 'creator_position', 
            'creator_position_name', 'creator_department_name', 'basis', 'basis_display',
            'amount', 'quantity', 'status', 'status_display', 'current_step_number',
            'created_at', 'updated_at', 'steps', 'is_my_turn'
        ]

    def get_document_name(self, obj):
        try:
            return DocumentType(obj.document_code).label
        except ValueError:
            return obj.document_code

    def get_is_my_turn(self, obj):
        request = self.context.get('request')
        if not request or not request.user or not hasattr(request.user, 'employee_profile'):
            return False
        
        # Check if request is PENDING and current active step requires user's position
        if obj.status != ApprovalStatus.PENDING:
            return False
            
        employee = request.user.employee_profile
        active_step = obj.steps.filter(step_number=obj.current_step_number, status=StepStatus.PENDING).first()
        if active_step and active_step.position_id == employee.position_id:
            return True
        return False


class DocumentSignatureSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    position_name = serializers.CharField(source='position.name', read_only=True)
    position_code = serializers.CharField(source='position.code', read_only=True)
    department_name = serializers.CharField(source='position.department.name', default='', read_only=True)
    signer_name = serializers.CharField(source='user.username', default='', read_only=True)
    signer_employee_name = serializers.CharField(source='user.employee_profile.full_name', default='', read_only=True)

    class Meta:
        model = DocumentSignature
        fields = [
            'id', 'document_code', 'document_id', 'document_number', 'step_number', 
            'role', 'role_display', 'position', 'position_name', 'position_code', 
            'department_name', 'user', 'signer_name', 'signer_employee_name', 
            'is_signed', 'signed_at', 'signature_draw', 'signature_image', 
            'ip_address', 'user_agent'
        ]


class ApprovalActionSerializer(serializers.Serializer):
    remarks = serializers.CharField(required=False, allow_blank=True, default='')


class ApprovalRequestSubmitSerializer(serializers.Serializer):
    document_code = serializers.ChoiceField(choices=DocumentType.choices)
    document_id = serializers.CharField(max_length=50)
    document_number = serializers.CharField(max_length=100)
    amount = serializers.DecimalField(max_digits=18, decimal_places=2, required=False, allow_null=True)
    quantity = serializers.DecimalField(max_digits=18, decimal_places=2, required=False, allow_null=True)

