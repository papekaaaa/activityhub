from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from post.models import Post # 1. Import โมเดล Post

# View สำหรับหน้าหลัก (ทุกคนเข้าได้)
def home_view(request):
    # 2. ดึงข้อมูลเฉพาะโพสต์ที่ได้รับการ "อนุมัติแล้ว" (APPROVED)
    posts = Post.objects.filter(status=Post.Status.APPROVED).order_by('-event_date')
    
    context = {
        'posts': posts
    }
    return render(request, 'home/homes.html', context)


# View สำหรับหน้ารายละเอียด (ต้อง Login)
@login_required # บังคับให้ต้อง Login ก่อนเข้าถึง View 
def post_detail_view(request, post_id):
    # 4. ดึงข้อมูลโพสต์ตาม id ที่ส่งมา ถ้าไม่เจอจะแสดงหน้า 404 Not Found
    post = get_object_or_404(Post, id=post_id)
    
    context = {
        'post': post
    }
    return render(request, 'home/post_detail.html', context)