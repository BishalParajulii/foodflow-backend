"""Review endpoints: public browse, authenticated write, rating summary."""

from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.mixins import SuccessResponseMixin
from apps.restaurants.models import Restaurant
from apps.reviews.models import Review
from apps.reviews.permissions import IsReviewAuthorOrReadOnly
from apps.reviews.serializers import ReviewSerializer


@extend_schema(tags=["Reviews"])
@extend_schema_view(
    list=extend_schema(summary="List reviews"),
    retrieve=extend_schema(summary="Get a review"),
    create=extend_schema(summary="Write a review (authenticated)"),
    partial_update=extend_schema(summary="Update your review"),
    update=extend_schema(summary="Replace your review"),
    destroy=extend_schema(summary="Delete your review"),
)
class ReviewViewSet(SuccessResponseMixin, viewsets.ModelViewSet):
    queryset = Review.objects.select_related("user", "restaurant", "order").filter(
        is_visible=True
    )
    serializer_class = ReviewSerializer
    permission_classes = [IsReviewAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["restaurant", "rating", "user"]
    search_fields = ["title", "comment"]
    ordering_fields = ["rating", "created_at"]
    ordering = ["-created_at"]
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]
    success_messages = {"create": "Review submitted successfully."}

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(summary="Rating summary for a restaurant")
    @action(detail=False, methods=["get"], url_path="summary")
    def summary(self, request):
        restaurant = get_object_or_404(Restaurant, pk=request.query_params.get("restaurant"))
        agg = Review.objects.filter(restaurant=restaurant, is_visible=True).aggregate(
            average=Avg("rating"), count=Count("id")
        )
        return Response(
            {
                "restaurant": str(restaurant.id),
                "restaurant_name": restaurant.name,
                "average_rating": round(agg["average"], 2) if agg["average"] is not None else None,
                "review_count": agg["count"],
            }
        )
