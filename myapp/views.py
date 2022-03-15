from sqlite3 import paramstyle
from django.utils import timezone
from django.shortcuts import redirect, render, resolve_url
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView, CreateView, DetailView, UpdateView, DeleteView, ListView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.core.paginator import Paginator

from .models import Post, Like, Category
from .forms import PostForm, LoginForm, SignUpForm, SearchForm


class OnlyMyPostMixin(UserPassesTestMixin):
    raise_exception = True
    def test_func(self):
        post = Post.objects.get(id = self.kwargs['pk'])
        return post.author == self.request.user


class OnlyPostCreate(UserPassesTestMixin):
    raise_exception = True
    def test_func(self):
        return self.request.user.is_authenticated


class Index(TemplateView):
    template_name = 'myapp/index.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        post_list = Post.objects.all().order_by('-created_at')[:6]
        context = {
            'post_list': post_list,
        }
        return context
    
    
class PostCreate(OnlyPostCreate, CreateView):
    model = Post
    form_class = PostForm
    success_url = reverse_lazy('myapp:index')
    template_name = 'myapp/post_form.html'
    
    def form_valid(self, form):
        form.instance.author_id = self.request.user.id
        return super(PostCreate, self).form_valid(form)
    
    def get_success_url(self):
        messages.success(self.request, 'New post has beed registered.')
        return resolve_url('myapp:index')
    

class PostDetail(DetailView):
    model = Post
    template_name = 'myapp/post_detail.html'
    
    def get_context_data(self, **kwargs):
        '''
        add things below into the object
        - like flag
        - posts have same category
        '''
        context = super().get_context_data(**kwargs)
        is_liked = Like.objects.filter(user = self.request.user).filter(post = context['object'].pk).count() > 0
        context['is_liked'] = is_liked
        
        category = Post.objects.get(id=self.kwargs['pk']).category
        posts = Post.objects.filter(category = category).exclude(id = self.kwargs['pk']).order_by('-created_at')[:5]
        context['posts'] = posts
        return context


class PostUpdate(OnlyMyPostMixin, UpdateView):
    model = Post
    form_class = PostForm 
    
    def get_success_url(self):
        messages.info(self.request, 'The Post has been updated.')
        return resolve_url('myapp:post_detail', pk=self.kwargs['pk'])
    
    
    
class PostDelete(OnlyMyPostMixin, DeleteView):
    model = Post
    
    def get_success_url(self):
        messages.info(self.request, 'The Post has been deleted.')
        return resolve_url('myapp:index')
    
    
class PostList(ListView):
    model = Post
    paginate_by  = 6
    
    def get_queryset(self):
        return Post.objects.all().order_by('-created_at')
    
    
class Login(LoginView):
    form_class = LoginForm
    template_name = 'myapp/login.html'

    
class Logout(LogoutView):
    template_name = 'myapp/logout.html'
    
    
class SignUp(CreateView):
    form_class = SignUpForm
    template_name = 'myapp/signup.html'
    success_url = reverse_lazy('myapp:index')
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        self.object = user
        messages.info(self.request, 'Your account has registered successfully.')
        return HttpResponseRedirect(self.get_success_url())


@login_required
def AddLike(request, post_id):
    post = Post.objects.get(id = post_id)
    is_liked = Like.objects.filter(user = request.user).filter(post = post_id).count()
    if is_liked > 0:
        messages.info(request, 'You already liked this post.')
    else:
        like = Like()
        like.user = request.user
        like.post = post
        like.save()
        messages.success(request, 'Added your liked articles!')
    return redirect('myapp:post_detail', post.id)


class CategoryList(ListView):
    model = Category
    template_name = 'myapp/category_list.html'
    
    
class CategoryDetail(DetailView):
    model = Category
    slug_field = 'name'
    slug_url_kwarg = 'name'
    template_name = 'myapp/category_detail.html'
    
    def get_context_data(self, **kwargs):
        category_name = Category.objects.get(name = self.kwargs['name'])
        posts = Post.objects.filter(category = category_name).order_by('-created_at')
        params = {
            'category_name': category_name,
            'posts': posts,
        }
        return params


def SearchPost(request):
    if request.method == 'POST':
        searchform = SearchForm(request.POST)
        
        if searchform.is_valid():
            search_word = searchform.cleaned_data['search_word']
            posts_hit = Post.objects.filter(Q(title__icontains = search_word)|
                                        Q(content__icontains = search_word))
            is_exist = posts_hit.count() > 0
            
        params = {
            'posts_hit': posts_hit,
            'is_exist': is_exist,
            'search_word': search_word,
        }
        
        return render(request, 'myapp/search.html', params)
    