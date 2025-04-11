from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("ws_conn/", views.make_ws_con, name="make websocket connection"),
    path("get-balance/", views.get_balance, name="get_balance"),
    path("place_order/", views.place_order, name="place a new order"),
]
