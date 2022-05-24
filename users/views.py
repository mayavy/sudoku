
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string

from django.contrib.auth import login
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from posts.models import CommentModel, SudokuModel

from .models import CustomUser
from .forms import RegistrationForm, UserEditForm
from .token import account_activation_token
from posts.html import My_Queryset


@login_required
def delete_user(request):
    if request.method == "POST":
        user = CustomUser.objects.get(username=request.user)
        user.is_active = False
        user.save()
        return redirect('users:login')
    return render(request, 'accounts/delete.html')


@login_required  # not in use
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)

        if user_form.is_valid():
            user_form.save()

    else:
        user_form = UserEditForm(instance=request.user)
    return render(request,
                  'accounts/update.html',
                  {'user_form': user_form})


@login_required
def profile(request):
    # custom view manager
    qs = SudokuModel.objects.filter(author=request.user)

    return render(request, 'accounts/profile.html',
                  {'section': 'profile', 'qs': My_Queryset(qs)})


def accounts_register(request):
    if request.method == 'POST':
        registerForm = RegistrationForm(request.POST)
        if registerForm.is_valid():
            user = registerForm.save(commit=False)
            user.email = registerForm.cleaned_data['email']
            user.set_password(registerForm.cleaned_data['password2'])
            user.is_active = False

            if not user.is_superuser:
                group, now_create = Group.objects.get_or_create(name='people')

                if now_create:  # assign permission first time
                    ct0 = ContentType.objects.get_for_model(
                        SudokuModel)
                    ct1 = ContentType.objects.get_for_model(
                        CommentModel)
                    permission = Permission.objects.filter(
                        Q(content_type=ct0) | Q(content_type=ct1))
                    # print(permission)
                    group.permissions.set(permission)

            current_site = get_current_site(request)
            subject = 'activate your account at _'
            message = render_to_string(
                'registration/account_activation_email.html',
                {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })
            user.email_user(subject=subject, message=message)
            user.save()  # form instance
            return HttpResponse('registeration accepted & activation link sent')

        else:
            return render(request, 'registration/register.html',
                          {'form': registerForm, 'invalid': 'forminvalid'})

    else:
        registerForm = RegistrationForm()
        return render(request, 'registration/register.html', {'form': registerForm})


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)

    except(TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()  # customuser instance
        # assign user to the group
        group = Group.objects.get(name='people')
        group.user_set.add(user)

        login(request, user)
        return redirect('login')

    else:
        return render(request, 'registration/activation_invalid.html')
