from django.urls import path
from .views import sudoku_list_view, sudoku_detail_view, home_view, about_view


app_name = 'posts'

urlpatterns = [
    path('home/', home_view, name='home'),
    path('listall/', sudoku_list_view, name='list'),
    path('detail/<uuid:pk>/', sudoku_detail_view, name='detail'),
    path('about/', about_view, name='about')
]
