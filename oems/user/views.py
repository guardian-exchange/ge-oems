from django.http import HttpResponse, JsonResponse
from django.utils.html import format_html
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, get_user_model
from .forms import SignupForm, LoginForm, StockConnectForm, PlaceOrderForm
from django.contrib.auth.decorators import login_required
from stocks.models import Stock
from user.models import UserStock, User
import websocket
import threading
import json
import os

# Environment variables
WS_HOST = os.environ.get("SM_HOST", "localhost")
WS_PORT = os.environ.get("SM_PORT", "8765")


def update_stock(message):
    """
    Update stock prices based on a dictionary where keys are stock names
    and values are the new prices.
    """
    for stock_name, new_price in message.items():
        updated_count = Stock.objects.filter(stock_name=stock_name).update(
            current_price=float(new_price)
        )
        if updated_count == 0:
            print(f"[Warning] Stock '{stock_name}' not found in DB.")
        else:
            print(f"[Info] Updated '{stock_name}' to price {new_price}.")


def do_place(user, stock_name, stock_quantity, stock_side):
    try:
        # Lock stock and user rows for consistency
        stock = Stock.objects.select_for_update().get(stock_name=stock_name)

        current_price = stock.current_price
        total_cost = current_price * int(stock_quantity)

        if stock_side.lower() == "buy":
            if total_cost > user.balance:
                print(
                    f"Insufficient balance, cost {total_cost} and balance {user.balance}"
                )
                return

            user.balance -= total_cost
            user.save()

            # Update or create UserStock
            user_stock, _ = UserStock.objects.get_or_create(user=user, stock=stock)
            user_stock.quantity += stock_quantity
            user_stock.save()

            print(f"Bought {stock_quantity} {stock_name} at {current_price} each.")

        elif stock_side.lower() == "sell":
            try:
                user_stock = UserStock.objects.select_for_update().get(
                    user=user, stock=stock
                )
            except UserStock.DoesNotExist:
                print(f"You don't own any {stock_name} to sell.")
                return

            if user_stock.quantity < stock_quantity:
                print(f"Not enough {stock_name} to sell.")
                return

            user_stock.quantity -= stock_quantity
            user_stock.save()

            user.balance += total_cost
            user.save()

            print(f"Sold {stock_quantity} {stock_name} at {current_price} each.")

        else:
            print("Invalid stock_side. Use 'buy' or 'sell'.")
            return

    except Stock.DoesNotExist:
        print(f"Stock '{stock_name}' not found.")
    except Exception as e:
        print(f"Error placing order: {e}")


def open_ws(stock_name):
    def on_message(ws, message):
        print(f"Received from WS: {json.loads(message)}")
        update_stock(json.loads(message))

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


def profile_view(request):
    if request.method != "GET":
        return HttpResponse(
            "Only GET is supported at endpoint /user/login/",
            status=400,
        )

    User = get_user_model()
    try:
        user_id = request.user.id
        user = User.objects.get(id=user_id)
        return render(
            request,
            "users/profile.html",
            {
                "user": user,
            },
        )
    except User.DoesNotExist:
        return HttpResponse(
            format_html(
                'User not found. Please <a href="/user/login/">login</a>.',
            ),
            status=400,
        )


# NOTE: Added for testing the endpoint
# from django.views.decorators.csrf import csrf_exempt
# @csrf_exempt
@login_required
def make_ws_con(request):
    if request.method == "POST":
        form = StockConnectForm(data=request.POST)
        if form.is_valid():
            stock_name = form.cleaned_data["stock_name"]
            open_ws(stock_name)  # Start WebSocket connection
            return HttpResponse(f"<h1>Making connection to {stock_name} ...</h1>")
    else:
        form = StockConnectForm()

    return render(request, "users/ws_conn_form.html", {"form": form})


@login_required
def place_order(request):
    if request.method == "POST":
        form = PlaceOrderForm(data=request.POST)
        if form.is_valid():
            stock_name = form.cleaned_data["stock_name"]
            stock_quantity = form.cleaned_data["stock_quantity"]
            stock_side = form.cleaned_data["stock_side"]
            do_place(request.user, stock_name, stock_quantity, stock_side)
            return HttpResponse(f"<h1>Placing order...</h1>")
    else:
        form = PlaceOrderForm()

    return render(request, "users/place_order_form.html", {"form": form})
