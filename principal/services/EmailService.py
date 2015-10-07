from principal.views import EmailViews


def send_email_create_user(user_create, request):

    for user in list(user_create.keys()):
        EmailViews.send_email_create_user(user, user_create[user], request)
