from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Party, PartyRole

UserLogin = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    role_type = serializers.ChoiceField(choices=[("CUSTOMER", "Customer"), ("ADMIN", "Admin")])

    class Meta:
        model = UserLogin
        fields = ("email", "password", "password2", "role_type")

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return attrs

    def create(self, validated_data):
        role_type = validated_data.pop("role_type")
        validated_data.pop("password2")

        # Create user (this auto-creates a Party in UserLoginManager)
        user = UserLogin.objects.create_user(**validated_data)

        # Assign PartyRole
        PartyRole.objects.create(party=user.party, role_type=role_type)

        return user


class UserSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()

    class Meta:
        model = UserLogin
        fields = ("id", "email", "is_active", "is_staff", "date_joined", "roles")

    def get_roles(self, obj):
        return [role.role_type for role in obj.party.roles.all()]
