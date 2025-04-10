from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

class LoginForm(AuthenticationForm):
    pass

class StockConnectForm(forms.Form):
    stock_name = forms.CharField(label="Stock Name", max_length=100)

class PlaceOrderForm(forms.Form):
    stock_name = forms.CharField(label="Stock Name", max_length=100)
    stock_quantity = forms.IntegerField(label="Stock Quantity", min_value=1, max_value=1000)
    stock_side = forms.CharField(label="Side", max_length=10)