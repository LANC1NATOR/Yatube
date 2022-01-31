from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page

from .models import Post, Group, User, Comment, Follow
from .forms import PostForm, CommentForm


# @cache_page(20, key_prefix='index_page')
def index(request):
    post_list = Post.objects.select_related('author', 'group')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'index.html',
                  {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group
                              .objects
                              .filter(slug=slug)
                              .select_related())
    post_list = Post\
        .objects\
        .filter(group=group)\
        .select_related('author', 'group')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'group': group, 'page': page, 'paginator': paginator}
    return render(request, 'group.html', context)


def new_post(request):
    if request.user.is_authenticated:
        form = PostForm(request.POST or None, files=request.FILES or None, )
        if request.method == 'POST':
            if form.is_valid():
                form = form.save(commit=False)
                form.author = request.user
                form.save()
                return redirect('index')
            return render(request, 'new_post.html', {'form': form})
        return render(request, 'new_post.html', {'form': form})
    return redirect('index')


def profile(request, username):
    author = get_object_or_404(User
                               .objects
                               .filter(username=username)
                               .select_related())
    post_list = Post\
        .objects\
        .filter(author=author)\
        .select_related('author', 'group')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = author.following.exists()
    return render(request, 'profile.html', {'page': page,
                                            'paginator': paginator,
                                            'author': author,
                                            'post_list': post_list,
                                            'following': following,
                                            })


def post_view(request, username, post_id):
    author = get_object_or_404(User
                               .objects
                               .filter(username=username)
                               .select_related())
    post = get_object_or_404(Post
                             .objects
                             .filter(author=author, id=post_id)
                             .select_related('author', 'group'))
    posts_count = Post\
        .objects\
        .filter(author=author)\
        .select_related('author', 'group')\
        .count()
    form = CommentForm()
    items = Comment.objects.filter(post=post).select_related('author')
    return render(request, 'post.html', {'author': author, 'post': post,
                                         'posts_count': posts_count,
                                         'form': form, 'items': items})


def post_edit(request, username, post_id):
    if request.user.username != username:
        return redirect('post', username=username, post_id=post_id)
    post = get_object_or_404(Post
                             .objects
                             .filter(author__username=username, id=post_id)
                             .select_related('author', 'group'))
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('post', username=username, post_id=post_id)
        return render(request, 'new_post.html',
                      {'form': form, 'post': post, 'username': username})
    return render(request, 'new_post.html', {'form': form, 'post': post,
                                             'username': username})


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)


def add_comment(request, username, post_id):
    if request.user.is_authenticated:
        form = CommentForm(request.POST or None)
        post = get_object_or_404(Post
                                 .objects
                                 .filter(author__username=username, id=post_id)
                                 .select_related('author', 'group'))
        if request.method == 'POST':
            if form.is_valid():
                form = form.save(commit=False)
                form.post = post
                form.author = request.user
                form.save()
                return redirect('post', username=username, post_id=post_id)
            return render(request, 'comments.html', {'form': form})
        return render(request, 'comments.html', {'form': form})
    return redirect('post', username=username, post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, "follow.html",
                  {'page': page, 'paginator': paginator})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User
                               .objects
                               .filter(username=username)
                               .select_related())
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    Follow\
        .objects\
        .filter(author__username=username, user=request.user)\
        .delete()
    return redirect('profile', username=username)