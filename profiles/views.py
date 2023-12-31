from django.db.models import Count
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from travel_social.permissions import IsOwnerOrReadOnly
from .models import Profile
from .serializers import ProfileSerializer


def get_profile_stats():
    return Profile.objects.annotate(
        posts_count=Count("owner__post", distinct=True),
        followers_count=Count("owner__followed", distinct=True),
        following_count=Count("owner__follower", distinct=True),
    )


class ProfileList(generics.ListAPIView):
    """
    List all profiles.
    No create view as profile creation is handled by django signals.
    """

    queryset = get_profile_stats().order_by("-created_at")
    serializer_class = ProfileSerializer
    filter_backends = [
        filters.OrderingFilter,
        DjangoFilterBackend,
    ]
    filterset_fields = [
        'owner__follower__followed__profile',  # Profiles that follow the user
        'owner__followed__owner__profile'      # Profiles the user follows
    ]
    ordering_fields = [
        "posts_count",
        "followers_count",
        "following_count",
        "owner__following__created_at",
        "owner__followed__created_at",
    ]


class ProfileDetail(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update a profile if you're the owner.
    """

    permission_classes = [IsOwnerOrReadOnly]
    queryset = get_profile_stats()
    serializer_class = ProfileSerializer
