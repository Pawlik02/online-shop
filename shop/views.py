from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.views import generic, View
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin
from .forms import RegisterForm, LoginForm, AddToCartForm, OrderForm
from .models import Profile, User, Category, Product, Cart, CartItem, Order

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

    def get_context_data(self, **kwargs):
        context = super(ProductDetail, self).get_context_data(**kwargs)
        context["form"] = AddToCartForm(available_quantity=self.get_object().available_quantity)
        return context

    def get_object(self):
        category = Category.objects.get(name=self.kwargs["category"])
        if "slug" in self.kwargs:
            product = Product.objects.get(slug=self.kwargs["slug"], id=self.kwargs["id"], category=category)
        else:
            product = Product.objects.get(id=self.kwargs["id"], category=category)
        return product

class ProductForm(SingleObjectMixin, FormView):
    template_name = "shop/product_detail.html"
    form_class = AddToCartForm
    model = Product

    def get_form(self):
        form_class = self.get_form_class()
        return form_class(self.get_object().available_quantity, **self.get_form_kwargs())
        
    def form_valid(self, form):
        quantity = form.cleaned_data["quantity"]
        return HttpResponseRedirect(reverse("shop:cart_add", kwargs={"product_id":self.kwargs["id"], "quantity":quantity}))

    def get_object(self):
        category = Category.objects.get(name=self.kwargs["category"])
        if "slug" in self.kwargs:
            product = Product.objects.get(slug=self.kwargs["slug"], id=self.kwargs["id"], category=category)
        else:
            product = Product.objects.get(id=self.kwargs["id"], category=category)
        return product

class ProductView(View):
    def get(self, request, *args, **kwargs):
        view = ProductDetail.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = ProductForm.as_view()
        return view(request, *args, **kwargs)

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
        form = RegisterForm
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
        form = LoginForm
    return render(request, "shop/login.html", {"form":form, "if_error":if_error})

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("shop:index"))

@login_required
def cart(request):
    cart = Cart.objects.get(profile=Profile.get_profile_by_request(request), ordered=False)
    cart_items = CartItem.objects.filter(cart=cart)
    return render(request, "shop/cart.html", {"cart_items":cart_items, "total_price":get_total_price(cart_items)})

@login_required
def cart_add(request, product_id, quantity):
    cart = Cart.objects.get(profile=Profile.get_profile_by_request(request), ordered=False)
    product = Product.objects.get(id=product_id)
    if not CartItem.objects.filter(cart=cart, product=product).exists():
        CartItem(cart=cart, product=product, ordered_quantity=quantity).save()
    return HttpResponseRedirect(reverse("shop:products", kwargs={"category":product.category.name, "id":product.id, "slug":product.slug}))

@login_required
def cart_del(request, item_id):
    CartItem.objects.get(id=item_id).delete()
    return HttpResponseRedirect(reverse("shop:cart"))

@login_required
def cart_update(request, item_id):
    cart_item = CartItem.objects.get(id=item_id)
    cart_item.ordered_quantity = request.POST["quantity"]
    cart_item.save()
    return HttpResponseRedirect(reverse("shop:cart"))

@login_required
def order(request):
    profile = Profile.get_profile_by_request(request)
    cart = Cart.objects.get(profile=profile, ordered=False)
    cart_items = CartItem.objects.filter(cart=cart)
    total_price = get_total_price(cart_items)
    if not cart_items:
        return HttpResponseRedirect(reverse("shop:cart"))
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            address = form.cleaned_data["address"]
            email = form.cleaned_data["email"]
            phone = form.cleaned_data["phone"]
            order = Order(profile=profile, cart=cart, first_name=first_name, last_name=last_name, address=address, email=email, phone=phone)
            order.save()
            cart.ordered = True
            cart.save()
            new_cart = Cart(profile=profile)
            new_cart.save()
            for item in cart_items:
                item.product.available_quantity -= item.ordered_quantity
                item.product.save()
            return HttpResponseRedirect(reverse("shop:summary"))
    else:
        form = OrderForm
    return render(request, "shop/order.html", {"cart":cart, "cart_items":cart_items, "form":form, "total_price":total_price})

@login_required
def summary(request):
    orders = Order.objects.all()
    carts = Cart.objects.filter(profile=Profile.get_profile_by_request(request), ordered=True)
    total_price = []
    for i in range(len(carts)):
        total_price.append(get_total_price(carts[i].cartitem_set.all()))
    orders = zip(orders, total_price)
    return render(request, "shop/summary.html", {"orders":orders})

# Custom functions

def get_total_price(cart_items):
    total_price = 0
    for i in range(len(cart_items)):
        total_price += cart_items[i].get_price()
    return total_price