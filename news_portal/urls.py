"""
URL configuration for news_portal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, include
from news.views import PostsList, PostDetail, SearchPosts, NewsCreateView, ArticleCreateView, NewsUpdateView, \
    ArticleUpdateView, PostDeleteView, subscriptions


urlpatterns = [
    path('admin/', admin.site.urls),
    path('pages/', include('django.contrib.flatpages.urls')),
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('accounts.urls')),
    path('news/', PostsList.as_view(), name='news_list'),  # Список новостей
    path('news/<int:pk>/', PostDetail.as_view(), name='news_detail'),  # Детали новости
    path('search/', SearchPosts.as_view()),
    path('news/create/', NewsCreateView.as_view(), name='news_create'),
    path('articles/create', ArticleCreateView.as_view(), name='article_create'),
    path('news/<int:pk>/edit/', NewsUpdateView.as_view(), name='news_update'),
    path('articles/<int:pk>/edit', ArticleUpdateView.as_view(), name='article_update'),
    path('news/<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
    path('articles/<int:pk>/delete', PostDeleteView.as_view(), name='post_delete'),
    path('<pk>', PostDetail.as_view(), name='news_detail'),
    path('search/<pk>', PostDetail.as_view(), name='news_detail'),
    path('subscriptions/', subscriptions, name='subscriptions'),

]
