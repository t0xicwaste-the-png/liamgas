from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.http import JsonResponse
from django import forms
from .models import ChatRoom, Message, UserProfile

class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture']

@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfilePictureForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile picture updated!')
            return redirect('profile')
    else:
        form = ProfilePictureForm(instance=profile)

    return render(request, 'profile.html', {'form': form, 'profile': profile})

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('chat_rooms')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def chat_rooms(request):
    rooms = ChatRoom.objects.all().order_by('-created_at')
    return render(request, 'chat_rooms.html', {'rooms': rooms})

@login_required
def chat_room(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    # Get recent messages (last 50 for performance)
    messages_list = Message.objects.filter(room=room).order_by('-timestamp')[:50][::-1]
    return render(request, 'chat_room.html', {'room': room, 'messages': messages_list})

@login_required
def create_room(request):
    if not request.user.is_superuser:
        messages.error(request, 'Only administrators can create chat rooms.')
        return redirect('chat_rooms')

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        if name:
            ChatRoom.objects.create(name=name, description=description, created_by=request.user)
            messages.success(request, 'Chat room created!')
            return redirect('chat_rooms')
    return render(request, 'create_room.html')

@login_required
def send_message(request, room_id):
    if request.method == 'POST':
        room = get_object_or_404(ChatRoom, id=room_id)
        content = request.POST.get('content')
        if content:
            message = Message.objects.create(room=room, user=request.user, content=content)
            return JsonResponse({
                'success': True,
                'message': {
                    'id': message.id,
                    'user': request.user.username,
                    'content': message.content,
                    'timestamp': message.timestamp.isoformat(),
                    'profile_picture': message.user.userprofile.profile_picture.url if message.user.userprofile.profile_picture else None
                }
            })
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def get_messages(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    after_id = request.GET.get('after', 0)

    messages = Message.objects.filter(
        room=room,
        id__gt=after_id
    ).order_by('timestamp').select_related('user', 'user__userprofile')

    message_data = []
    for message in messages:
        message_data.append({
            'id': message.id,
            'user': message.user.username,
            'content': message.content,
            'timestamp': message.timestamp.isoformat(),
            'profile_picture': message.user.userprofile.profile_picture.url if message.user.userprofile.profile_picture else None
        })

    return JsonResponse({'messages': message_data})