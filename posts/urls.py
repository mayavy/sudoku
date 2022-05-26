from django.urls import path
from .views import SudokuListView, SudokuDetailView, HomeView, AboutView


app_name = 'posts'

urlpatterns = [
    path('home/', HomeView.as_view(), name='home'),
    path('listall/', SudokuListView.as_view(), name='list'),
    path('detail/<uuid:pk>/', SudokuDetailView.as_view(), name='detail'),
    path('about/', AboutView.as_view(), name='about')
]
