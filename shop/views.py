from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from django.views import generic
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, LoginForm
from .models import Profile, User, Category, Product, Cart, CartItem

def index(request):
    return render(request, "shop/index.html")

class CategoriesView(generic.DetailView):
    model = Category

    def get_products(self):
        products = []
        products = self.get_object().product_set.all()
        return products

class ProductDetail(generic.DetailView):
    model = Product

    def get_object(self):
        category = Category.objects.get(name=self.kwargs["category"])
        if "slug" in self.kwargs:
            product = Product.objects.get(slug=self.kwargs["slug"], id=self.kwargs["id"], category=category)
        else:
            product = Product.objects.get(id=self.kwargs["id"], category=category)
        return product
    
def contact(request):
    return render(request, "shop/contact.html")

def register(request):
    if_error = ""
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = make_password(form.cleaned_data["password"]) 
            if User.objects.filter(username=username).exists():
                if_error = "User with this username already exists!"
            else:
                user = User.objects.create(username=username, password=password)
                profile = Profile(user=user)
                profile.save()
                cart = Cart(profile=profile)
                cart.save()
                login(request, user)
                return HttpResponseRedirect(reverse("shop:index"))
    else:
        form = RegisterForm()
    return render(request, "shop/register.html", {"form":form, "if_error":if_error})

def login_view(request):
    next_url = request.GET.get("next")
    if_error = ""
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                if next_url:
                    return HttpResponseRedirect(next_url) 
                return HttpResponseRedirect(reverse("shop:index"))
            else:
                if_error = "Wrong username or password, try again!"
    else:
        form = LoginForm()
    return render(request, "shop/login.html", {"form":form, "if_error":if_error})

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("shop:index"))

@login_required
def cart(request):
    cart = Cart.objects.get(profile=get_profile(request))
    cart_items = CartItem.objects.filter(cart=cart)
    return render(request, "shop/cart.html", {"cart_items":cart_items})

@login_required
def cart_add(request, product_id):
    cart = Cart.objects.get(profile=get_profile(request))
    product = Product.objects.get(id=product_id)
    if not CartItem.objects.filter(cart=cart, product=product).exists():
        CartItem(cart=cart, product=product).save()
    return HttpResponseRedirect(reverse("shop:products", kwargs={"category":product.category.name, "id":product.id, "slug":product.slug}))

@login_required
def cart_del(request, item_id):
    CartItem.objects.get(id=item_id).delete()
    return HttpResponseRedirect(reverse("shop:cart"))

# Custom functions
def get_profile(view_request):
    return Profile.objects.get(user=view_request.user.id)
