from rest_framework import serializers

from account.serializers import UserAccountSerializer

from .models import Advertisement, Category, House, RentRequest, Review


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class HouseSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=True, read_only=True)
    category_ids = serializers.ListField(write_only=True, required=False)
    owner = UserAccountSerializer(read_only=True)

    class Meta:
        model = House
        fields = "__all__"

    def create(self, validated_data):
        category_ids = validated_data.pop("category_ids", [])
        house = House.objects.create(**validated_data)
        house.category.set(category_ids)
        return house

    def update(self, instance, validated_data):
        category_ids = validated_data.pop("category_ids", None)
        instance = super().update(instance, validated_data)
        if category_ids is not None:
            instance.category.set(category_ids)
        return instance


class ReviewSerializer(serializers.ModelSerializer):
    user = UserAccountSerializer(read_only=True)

    class Meta:
        model = Review
        fields = "__all__"
        # fields = ["id", "user", "rating", "text", "created_at"]
        read_only_fields = ["user", "created_at"]


class AdvertisementSerializer(serializers.ModelSerializer):
    house = HouseSerializer(read_only=True)
    house_id = serializers.IntegerField(write_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Advertisement
        fields = "__all__"
        # fields = ["id", "house", "house_id", "is_approved", "is_rented", "reviews"]
        read_only_fields = ["is_approved", "is_rented"]


class RentRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = RentRequest
        fields = "__all__"
        read_only_fields = ["requested_by", "status", "created_at"]


class RentRequestShowSerializer(serializers.ModelSerializer):
    advertisement = AdvertisementSerializer(read_only=True)
    requested_by = UserAccountSerializer(read_only=True)

    class Meta:
        model = RentRequest
        fields = "__all__"
        read_only_fields = ["requested_by", "status", "created_at"]
