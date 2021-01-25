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
    path("cart-add/<product_id>/<quantity>/", views.cart_add, name="cart_add"),
    path("cart-del/<item_id>/", views.cart_del, name="cart_del"),
    path("cart-update/<item_id>/", views.cart_update, name="cart_update"),
    path("order/", views.order, name="order"),
    path("payment/", views.payment, name="payment"),
    path("<slug:slug>/", views.CategoriesView.as_view(), name="categories"),
    path("<category>/<int:id>-<slug:slug>/", views.ProductView.as_view(), name="products"),
    path("<category>/<int:id>/", views.ProductView.as_view(), name="products")
]