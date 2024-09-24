from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AcceptRentRequest,
    AdminAdvertisedHouseViewSet,
    AdvertisedHouseViewSet,
    AdvertiseRequestViewSet,
    ApproveAdvertisementViewSet,
    CategoryViewSet,
    FavoritesAdvertisementsViewSet,
    HandleRentRequestViewSet,
    HouseViewSet,
    RentRequestViewSet,
    ReviewViewSet,
    UserHouseViewSet,
)

router = DefaultRouter()

router.register("list", HouseViewSet, basename="house")
router.register("category", CategoryViewSet, basename="category")
router.register("my-houses", UserHouseViewSet, basename="user-house")
router.register(
    "advertisements/list", AdvertisedHouseViewSet, basename="advertisement_list"
)
router.register(
    "favorites_advertisements",
    FavoritesAdvertisementsViewSet,
    basename="favorites_advertisements",
)
router.register(
    "create-advertisement",
    AdvertiseRequestViewSet,
    basename="create-advertisement",
)
router.register(
    "approve-advertisement",
    ApproveAdvertisementViewSet,
    basename="approve-advertisement",
)

router.register(
    "admin-house-list", AdminAdvertisedHouseViewSet, basename="admin-adverise-list"
)
router.register("request-rent", HandleRentRequestViewSet, basename="request-rent")
router.register("show-rent", RentRequestViewSet, basename="show-rent")
router.register("review", ReviewViewSet, basename="review")


urlpatterns = [
    path("", include(router.urls)),
    path(
        "accept-rent-request/<int:rent_request_id>/",
        AcceptRentRequest.as_view(),
        name="accept-rent-request",
    ),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
