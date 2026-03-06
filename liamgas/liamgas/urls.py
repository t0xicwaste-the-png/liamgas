from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('chat/', views.chat_rooms, name='chat_rooms'),
    path('chat/<int:room_id>/', views.chat_room, name='chat_room'),
    path('chat/<int:room_id>/send/', views.send_message, name='send_message'),
    path('chat/<int:room_id>/messages/', views.get_messages, name='get_messages'),
    path('chat/create/', views.create_room, name='create_room'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)