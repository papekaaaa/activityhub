from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from post.models import Post

def index_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'home/index.html')

def map_view(request):
    return render(request, 'home/map.html')

def about_view(request):
    return render(request, 'home/about.html')

def home_view(request):
    posts = Post.objects.filter(status=Post.Status.APPROVED).order_by('-event_date')
    categories = [c[0] for c in Post.CATEGORY_CHOICES]
    selected_category = request.GET.get('category')

    if selected_category:
        posts = posts.filter(category=selected_category)

    context = {
        'posts': posts,
        'categories': categories,
        'selected_category': selected_category,
    }
    return render(request, 'home/homes.html', context)


def category_view(request):
    category_type = request.GET.get('type')
    posts = Post.objects.filter(status=Post.Status.APPROVED)
    if category_type:
        posts = posts.filter(category=category_type)

    context = {
        'posts': posts,
        'selected_category': category_type,
    }
    return render(request, 'home/category.html', context)


@login_required
def post_detail_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'home/post_detail.html', {'post': post})
