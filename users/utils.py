from users.models import UserAccount


def get_user_account(user_pk):
    """
    The function to check and get user account if it exists.
    :param user_pk: user account UUID.
    :return: UserAccount instance if exists, if not - Http404 Error with message.
    """
    try:
        return UserAccount.objects.get(user_id=user_pk)
    except UserAccount.DoesNotExist:
        return None
