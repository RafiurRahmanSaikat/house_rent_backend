from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import pagination, status, viewsets
from rest_framework.permissions import (
    BasePermission,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from . import models, serializers


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_staff


class ResultsSetPagination(pagination.PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 100


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HouseViewSet(viewsets.ModelViewSet):
    queryset = models.House.objects.all()
    serializer_class = serializers.HouseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=request.user.account)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )


class AdvertiseRequestViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.AdvertisementSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            house_id = serializer.validated_data.get("house_id")
            try:
                house = models.House.objects.get(pk=house_id)
            except models.House.DoesNotExist:
                return Response(
                    {"error": "House not found."}, status=status.HTTP_404_NOT_FOUND
                )

            if models.Advertisement.objects.filter(house=house).exists():
                return Response(
                    {"error": "Advertisement for this house already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            advertisement = serializer.save()
            house.is_advertised = True
            house.save(update_fields=["is_advertised"])

            return Response(
                {
                    "message": "Advertisement created successfully.",
                    "advertisement_id": advertisement.id,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApproveAdvertisementViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    serializer_class = serializers.AdvertisementSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            house_id = serializer.validated_data.get("house_id")
            advertisement = models.Advertisement.objects.get(house=house_id)
            advertisement.is_approved = True
            advertisement.save()
            return Response(
                {"message": "Advertisement Approved."}, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# admin er sob
class AdminAdvertisedHouseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    queryset = models.Advertisement.objects.all()
    serializer_class = serializers.AdvertisementSerializer


class UserHouseViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.HouseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_account = self.request.user.account
        return models.House.objects.filter(owner=user_account)


class AdvertisedHouseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = models.Advertisement.objects.filter(is_approved=True, is_rented=False)
    serializer_class = serializers.AdvertisementSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["house__category"]

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(house__category__id=category)
        return queryset


class FavoritesAdvertisementsViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = models.Advertisement.objects.filter(is_approved=True)
    serializer_class = serializers.AdvertisementSerializer


class UserHouseViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.HouseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return models.House.objects.filter(owner=self.request.user.account)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = models.Review.objects.all()
    serializer_class = serializers.ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {"message": "You have to login."}, status=status.HTTP_401_UNAUTHORIZED
            )
        else:

            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                advertisement = serializer.validated_data.get("advertisement")
                advertisement = get_object_or_404(
                    models.Advertisement, pk=advertisement.id
                )
                review = serializer.save(
                    user=request.user.account, advertisement=advertisement
                )

                return Response(
                    {"message": "Review added successfully.", "review_id": review.id},
                    status=status.HTTP_201_CREATED,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HandleRentRequestViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.RentRequestSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            advertisement = serializer.validated_data.get("advertisement")
            print(advertisement)
            if advertisement.is_rented:
                return Response(
                    {"error": "This advertisement has already been rented."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if models.RentRequest.objects.filter(
                advertisement=advertisement, requested_by=request.user.account
            ).exists():
                return Response(
                    {
                        "error": "You have already sent a rent request for this advertisement."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer.save(requested_by=request.user.account)
            advertisement.is_requested = True
            advertisement.save(update_fields=["is_requested"])

            return Response(
                {"message": "Rent request sent successfully."},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AcceptRentRequest(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, rent_request_id):
        rent_request = get_object_or_404(models.RentRequest, id=rent_request_id)

        if request.user.account != rent_request.advertisement.house.owner:
            return Response(
                {"error": "You are not authorized to accept this request."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if rent_request.advertisement.is_rented:
            return Response(
                {"error": "This house is already rented."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        rent_request.status = "ACCEPTED"
        rent_request.save()

        models.RentRequest.objects.filter(
            advertisement=rent_request.advertisement, status="PENDING"
        ).update(status="REJECTED")

        advertisement = rent_request.advertisement
        advertisement.is_rented = True
        advertisement.save()

        return Response(
            {
                "message": "Rent request accepted successfully. Other pending requests have been rejected."
            },
            status=status.HTTP_200_OK,
        )


class RentRequestViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = models.RentRequest.objects.all()
    serializer_class = serializers.RentRequestShowSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(advertisement__house__owner=self.request.user.account)
