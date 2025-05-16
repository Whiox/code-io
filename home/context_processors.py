from home.models import UserProfile


def user_avatar(request):
    if request.user.is_authenticated:
        profile_owner = request.user
        user_profile, _ = UserProfile.objects.get_or_create(user=profile_owner)

        return {'user_profile': user_profile}
    return {}
