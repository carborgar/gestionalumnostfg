from principal.models import Administrador


def find_one(user_id):
    try:
        administrator = Administrador.objects.get(id=user_id)
    except Administrador.DoesNotExist:
        assert False
    return administrator
