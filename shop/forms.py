from django import forms

class RegisterForm(forms.Form):
    username = forms.CharField(label="Username", max_length=150)
    password = forms.CharField(widget=forms.PasswordInput(),label="Password", max_length=150)

class LoginForm(forms.Form):
    username = forms.CharField(label="Username", max_length=150)
    password = forms.CharField(widget=forms.PasswordInput(),label="Password", max_length=150)

class AddToCartForm(forms.Form):
    quantity = forms.DecimalField(label="Quantity", initial=1, min_value=1)

class OrderForm(forms.Form):
    first_name = forms.CharField(label="First name", max_length=150)
    last_name = forms.CharField(label="Last name", max_length=150)
    address = forms.CharField(label="Address", max_length=150)
    email = forms.EmailField(label="Email", max_length=150)
    phone = forms.CharField(label="Phone number", max_length=12)