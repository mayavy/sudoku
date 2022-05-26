from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import DeleteView, CreateView

from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string

from django.contrib.auth import login
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from posts.models import CommentModel, SudokuModel
from django.urls import reverse_lazy

from .models import CustomUser
from .forms import RegistrationForm, UserEditForm
from .token import account_activation_token
from posts.html import My_Queryset


class DeleteUserView(LoginRequiredMixin, DeleteView):
    model = CustomUser
    template_name = 'accounts/delete.html'
    # override post method -> only deactivate user
    success_url = reverse_lazy('users:login')

    def post(self, request, *args, **kwargs):  # by default DeleteView deletes User from database
        user = CustomUser.objects.get(id=kwargs['pk'])
        user.is_active = False
        user.save()
        return redirect(self.success_url)


class ProfileView(LoginRequiredMixin, ListView):
    model = SudokuModel
    template_name = 'accounts/profile.html'
    context_object_name = 'qs'

    def get_queryset(self):
        qs = SudokuModel.objects.filter(
            author__is_active=True).filter(author=self.request.user)
        my_qs = My_Queryset(qs)
        return my_qs


class AccountsRegisterView(CreateView):
    template_name = 'registration/register.html'
    success_template_name = 'registration/mail-sent.html'
    form_class = RegistrationForm

    def form_valid(self, form):
        """If the form is valid, save the associated model.
        but sets activation False"""

        user = form.save(commit=False)
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

        current_site = get_current_site(self.request)
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

        user = form.save()
        self.object = user

        return render(self.request, self.success_template_name)


class ActivateView(TemplateView):
    def get(self, request, *args, **kwargs):
        try:
            uidb64 = kwargs['uidb64']
            token = kwargs['token']
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except Exception as e:
            user = None
        if user != None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()  # customuser instance
            # assign user to the group
            group = Group.objects.get(name='people')
            group.user_set.add(user)

            login(request, user)
            return redirect('login')

        else:
            return render(request, 'registration/activation_invalid.html')
