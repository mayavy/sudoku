"""sudoku_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.http import Http404, HttpResponse
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http.response import HttpResponseRedirect
from django.views.static import serve


def index(request, *args, **kwargs):
    return HttpResponseRedirect('sudoku/home/', *args, **kwargs)


# def null(request, *args, **kwargs):
#     return HttpResponse('rESponsee')


# urlpatterns = [re_path(r'.', null)]
urlpatterns = [
    path('',   index),
    path('sudoku/', include('posts.urls', namespace='posts')),
    path('nimda/', admin.site.urls),
    path('account/', include('users.urls', namespace='users')),
    path('account/', include('django.contrib.auth.urls')),
    # re_path(r'static/(?P<path>.*)', serve,
    #         {'document_root': settings.STATIC_ROOT}),
    # ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

]
