from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import SignupForm, LoginForm, StockConnectForm
from django.contrib.auth.decorators import login_required
import websocket
import threading
import json
import os

# Environment variables
WS_HOST = os.environ.get("SM_HOST", "localhost")
WS_PORT = os.environ.get("SM_PORT", "8765")


def open_ws(stock_name):
    def on_message(ws, message):
        print(f"Received from WS: {message}")

    def on_error(ws, error):
        print(f"WebSocket error: {error}")

    def on_close(ws, close_status_code, close_msg):
        print("WebSocket closed")

    def on_open(ws):
        print(f"WebSocket opened for stock: {stock_name}")
        ws.send(json.dumps({"action": "subscribe", "stock": stock_name}))

    ws = websocket.WebSocketApp(
        f"ws://{WS_HOST}:{WS_PORT}",  # change this to your target
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )

    # Run WebSocket in background thread
    threading.Thread(target=ws.run_forever).start()

@login_required
def index(request):
    return render(request, "users/dashboard.html")
    # return HttpResponse(f"<h1>Welcome, {request.user.username}!</h1>")

def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/user/")
    else:
        form = SignupForm()
    return render(request, "users/signup.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("/user/")
    else:
        form = LoginForm()
    return render(request, "users/login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("login")

# NOTE: Added for testing the endpoint
from django.views.decorators.csrf import csrf_exempt
# @csrf_exemptgo.views.decorators.csrf import csrf_exempt
# @csrf_exem
def make_ws_con(request):
    if request.method == "POST":
        form = StockConnectForm(data=request.POST)
        if form.is_valid():
            # make request
            stock_name = form.cleaned_data["stock_name"]
            open_ws(stock_name)  # Start WebSocket connection
            return HttpResponse(f"<h1>Making Connection ...</h1>")
        else:
            form = StockConnectForm()
        return render(request, "users/ws_conn_form.html", {"form": form})
    else:
        return HttpResponse(f"Only POST method is accepted!")
