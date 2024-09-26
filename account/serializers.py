from django.contrib.auth.models import User
from rest_framework import serializers

from .models import UserAccount


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    account_type = serializers.ChoiceField(
        choices=[("Admin", "Admin"), ("User", "User")]
    )
    address = serializers.CharField(required=True)
    image = serializers.CharField(required=True)
    mobile_number = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "confirm_password",
            "account_type",
            "address",
            "image",
            "mobile_number",
        ]

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords must match."}
            )
        if User.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError({"email": "Email already exists."})
        return data

    def create(self, validated_data):

        validated_data.pop("confirm_password")

        user = User(
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.set_password(validated_data["password"])
        user.is_active = False
        user.save()

        UserAccount.objects.create(
            user=user,
            account_type=validated_data["account_type"],
            address=validated_data["address"],
            image=validated_data["image"],
            mobile_number=validated_data["mobile_number"],
        )

        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=16, required=True)
    password = serializers.CharField(max_length=32, required=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]


class UserAccountSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserAccount

        fields = [
            "id",
            "user",
            "account_type",
            "address",
            "image",
            "mobile_number",
            "is_verified",
            "favourites",
        ]
