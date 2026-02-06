from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils.timezone import localtime

from zoneinfo import ZoneInfo  # ✅ เพิ่ม

from users.models import User
from post.models import Post
from .models import ChatRoom, ChatMembership, ChatMessage

BKK_TZ = ZoneInfo("Asia/Bangkok")  # ✅ เพิ่ม


@login_required
def inbox_view(request):
    """
    กล่องข้อความ: แสดงทุกห้องแชทที่ user เป็นสมาชิก
    ทั้งแชทกลุ่มกิจกรรม และแชทส่วนตัว (DM)
    """
    memberships = ChatMembership.objects.filter(
        user=request.user
    ).select_related('room', 'room__post')

    rooms_data = []

    for m in memberships:
        room = m.room
        title = ''
        subtitle = ''
        avatar_url = None
        link_url = '#'

        if room.room_type == 'GROUP':
            post = room.post
            if post and post.image:
                avatar_url = post.image.url
            title = room.name or (post.title if post else 'แชทกลุ่มกิจกรรม')
            subtitle = 'แชทกลุ่มกิจกรรม'
            if post:
                link_url = reverse('chat:activity_chat', args=[post.id])

        else:  # DM
            other_membership = (
                ChatMembership.objects
                .filter(room=room)
                .exclude(user=request.user)
                .select_related('user', 'user__profile')
                .first()
            )
            other_user = other_membership.user if other_membership else None

            if other_user:
                title = other_user.get_full_name() or other_user.username
                subtitle = 'ข้อความส่วนตัว'
                if hasattr(other_user, 'profile') and other_user.profile.profile_picture:
                    avatar_url = other_user.profile.profile_picture.url
                link_url = reverse('chat:dm_chat', args=[other_user.id])
            else:
                title = 'แชทส่วนตัว'
                subtitle = 'DM'

        last_msg = ChatMessage.objects.filter(
            room=room
        ).order_by('-created_at').first()

        if last_msg:
            content = last_msg.content or ''
            last_text = content[:60] + ('…' if len(content) > 60 else '')
            # ✅ ให้ last_time เป็นเวลาไทยด้วย (กันหน้า inbox เพี้ยน)
            last_time = localtime(last_msg.created_at, timezone=BKK_TZ)
        else:
            last_text = ''
            last_time = None

        rooms_data.append({
            'room': room,
            'title': title,
            'subtitle': subtitle,
            'avatar_url': avatar_url,
            'link_url': link_url,
            'last_message': last_text,
            'last_time': last_time,
            'is_group': (room.room_type == 'GROUP'),
        })

    rooms_data.sort(
        key=lambda r: r['last_time'].timestamp() if r['last_time'] else 0,
        reverse=True
    )

    return render(request, 'chat/inbox.html', {'rooms': rooms_data})


@login_required
def activity_chat_view(request, post_id):
    """
    แชทกลุ่มของกิจกรรม
    - 1 โพสต์ = 1 ห้องแชท GROUP
    - ถ้ายังไม่เป็นสมาชิก จะเพิ่มเข้าห้องให้
    """
    post = get_object_or_404(Post, id=post_id)

    room, created = ChatRoom.objects.get_or_create(
        room_type='GROUP',
        post=post,
        defaults={
            'name': post.title,
            'created_by': post.organizer,
        }
    )

    ChatMembership.objects.get_or_create(
        room=room,
        user=request.user,
        defaults={'is_admin': False},
    )

    # รองรับ POST แบบเดิม (ข้อความล้วน) เผื่อ fallback
    if request.method == "POST":
        text = request.POST.get("content", "").strip()
        file = request.FILES.get("file")
        if text or file:
            ChatMessage.objects.create(
                room=room,
                sender=request.user,
                content=text,
                attachment=file
            )
        return redirect('chat:activity_chat', post_id=post.id)

    messages_qs = ChatMessage.objects.filter(
        room=room
    ).select_related('sender').order_by('created_at')

    return render(
        request,
        'chat/chat.html',
        {
            'room': room,
            'post': post,
            'other_user': None,
            'is_group': True,
            'chat_messages': messages_qs,  # ✅ เปลี่ยนชื่อกันชนกับ Django messages
        },
    )


@login_required
def dm_chat_view(request, user_id):
    """
    แชทส่วนตัว (DM) ระหว่างเรา กับ user อีกคนหนึ่ง
    - ถ้าไม่มีห้อง จะสร้างห้องใหม่ + membership 2 คน
    """
    other_user = get_object_or_404(User, id=user_id)

    if other_user == request.user:
        return redirect('profile')

    my_room_ids = set(
        ChatMembership.objects.filter(
            user=request.user
        ).values_list('room_id', flat=True)
    )

    other_room_ids = set(
        ChatMembership.objects.filter(
            user=other_user
        ).values_list('room_id', flat=True)
    )

    common_ids = list(my_room_ids & other_room_ids)
    room = None
    if common_ids:
        room = ChatRoom.objects.filter(
            id__in=common_ids,
            room_type='DM',
        ).first()

    if not room:
        room = ChatRoom.objects.create(
            room_type='DM',
            name='ข้อความส่วนตัว',
            created_by=request.user,
        )
        ChatMembership.objects.bulk_create([
            ChatMembership(room=room, user=request.user, is_admin=False),
            ChatMembership(room=room, user=other_user, is_admin=False),
        ])

    # รองรับ POST แบบเดิม (ข้อความล้วน) เผื่อ fallback
    if request.method == "POST":
        text = request.POST.get("content", "").strip()
        file = request.FILES.get("file")
        if text or file:
            ChatMessage.objects.create(
                room=room,
                sender=request.user,
                content=text,
                attachment=file
            )
        return redirect('chat:dm_chat', user_id=other_user.id)

    messages_qs = ChatMessage.objects.filter(
        room=room
    ).select_related('sender').order_by('created_at')

    return render(
        request,
        'chat/chat.html',
        {
            'room': room,
            'post': None,
            'other_user': other_user,
            'is_group': False,
            'chat_messages': messages_qs,  # ✅ เปลี่ยนชื่อกันชน
        },
    )


@login_required
@require_POST
def upload_message_view(request, room_id):
    """
    ✅ อัปโหลดรูป/ไฟล์ผ่าน HTTP แล้ว broadcast ไปห้องแชทผ่าน Channels
    """
    room = get_object_or_404(ChatRoom, id=room_id)

    # เช็คสมาชิกห้อง (กันยิงมั่ว)
    if not ChatMembership.objects.filter(room=room, user=request.user).exists():
        return JsonResponse({"ok": False, "error": "not_member"}, status=403)

    text = (request.POST.get("content") or "").strip()
    file = request.FILES.get("file")

    if not text and not file:
        return JsonResponse({"ok": False, "error": "empty"}, status=400)

    msg = ChatMessage.objects.create(
        room=room,
        sender=request.user,
        content=text,
        attachment=file
    )

    # ตรวจว่าเป็นรูปไหม
    is_image = False
    if msg.attachment:
        is_image = msg.is_image()

    # ✅ บังคับเวลาไทย
    dt_local = localtime(msg.created_at, timezone=BKK_TZ)

    payload = {
        "type": "chat_message",  # ✅ ให้ตรงกับ handler ใน consumer
        "message": msg.content or "",
        "sender_id": request.user.id,
        "sender_name": request.user.get_full_name() or request.user.username,
        "created_at": dt_local.strftime("%d/%m/%Y %H:%M"),  # ✅ เวลาไทย
        "created_at_iso": dt_local.isoformat(),             # ✅ เผื่อ JS ใช้
        "file_url": msg.attachment.url if msg.attachment else "",
        "file_name": (msg.attachment.name.split("/")[-1] if msg.attachment else ""),
        "is_image": is_image,
    }

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(f"chat_{room_id}", payload)

    return JsonResponse({"ok": True})
