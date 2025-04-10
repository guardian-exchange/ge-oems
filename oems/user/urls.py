from django.urls import path
from .views import signup_view, login_view, logout_view, make_ws_con, place_order

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("ws_conn/", make_ws_con, name="make websocket connection"),
    path("place_order/", place_order, name="plae a new order"),
]
