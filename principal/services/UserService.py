from django.contrib.auth.models import User, Permission
from django.db.models import Q
from django.shortcuts import get_object_or_404
from principal.services import SubjectService


def find_by_username(username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = None
    return user


def find_all():
    perm_admin = Permission.objects.get(codename='administrator')
    return User.objects.filter(~Q(user_permissions=perm_admin)).order_by('username')


def search(search_text):
    perm_admin = Permission.objects.get(codename='administrator')
    return User.objects.filter(
        ~Q(user_permissions=perm_admin) &
        (
            Q(username__icontains=search_text) |
            Q(first_name__icontains=search_text)
        )).order_by('username')


def find_one(user_id):
    return get_object_or_404(User, id=user_id)


def delete(user):
    user.delete()


def rollback(user_create, student_link, lecturer_link, subject_id):

    subject = SubjectService.find_one(subject_id)

    for student in student_link:
        student.asignaturas.remove(subject)

    for lecturer in lecturer_link:
        lecturer.imparteasignatura_set.all().get(profesor_id=lecturer.id, asignatura_id=subject.id).delete()

    for user in user_create:
        delete(user)


def rollback_users(user_create):

    for user in list(user_create.keys()):
        delete(user)


def save_password(user, password):

    user.set_password(password)
    user.save()
    return user
