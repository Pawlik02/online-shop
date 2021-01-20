from django.urls import path
from . import views

app_name = "shop"
urlpatterns = [
    path("", views.index, name="index"),
    path("contact/", views.contact, name="contact"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login_view"),
    path("logout/", views.logout_view, name="logout_view"),
    path("cart/", views.cart, name="cart"),
    path("cart-add/<product_id>", views.cart_add, name="cart_add"),
    path("cart-del/<item_id>", views.cart_del, name="cart_del"),
    path("<slug:slug>/", views.CategoriesView.as_view(), name="categories"),
    path("<category>/<int:id>-<slug:slug>/", views.ProductDetail.as_view(), name="products"),
    path("<category>/<int:id>/", views.ProductDetail.as_view(), name="products")
]