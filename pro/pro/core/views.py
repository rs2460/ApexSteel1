from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Product, Wishlist, CartItem, Order, OrderItem, Review
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all().order_by('-created_at')
    user_has_purchased = False
    if request.user.is_authenticated:
        user_has_purchased = Order.objects.filter(user=request.user, items__product=product, status='Delivered').exists()

    context = {
        'product': product,
        'reviews': reviews,
        'user_has_purchased': user_has_purchased
    }
    return render(request, 'product_detail.html', context)

@login_required
def submit_review(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        Review.objects.update_or_create(
            product=product, 
            user=request.user,
            defaults={'rating': rating, 'comment': comment}
        )
        messages.success(request, "Your review has been submitted!")
    return redirect('product_detail', product_id=product_id)


import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

def index(request):
    return render(request, 'index.html')

def about_view(request):
    return render(request, 'about.html')

def contact_view(request):
    return render(request, 'contact.html')

def product_list(request):
    products = Product.objects.all()
    wishlisted_product_ids = []
    if request.user.is_authenticated:
        wishlisted_product_ids = list(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))
    return render(request, 'products.html', {
        'products': products,
        'wishlisted_product_ids': wishlisted_product_ids
    })

def toggle_wishlist(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'login_required'}, status=403)
    
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
        
        if not created:
            wishlist_item.delete()
            status = 'removed'
        else:
            status = 'added'
            
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        return JsonResponse({'status': status, 'wishlist_count': wishlist_count})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    shipping = 0 # As per screenshot
    total = subtotal + shipping
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping': shipping,
        'total': total
    })

@login_required
def update_cart_quantity(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        action = request.POST.get('action')
        product = get_object_or_404(Product, id=product_id)
        cart_item = get_object_or_404(CartItem, user=request.user, product=product)
        
        if action == 'increase':
            cart_item.quantity += 1
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
            else:
                cart_item.delete()
                return JsonResponse({'status': 'removed', 'cart_count': CartItem.objects.filter(user=request.user).count()})
        
        cart_item.save()
        
        # Calculate new totals
        cart_items = CartItem.objects.filter(user=request.user)
        subtotal = sum(item.product.price * item.quantity for item in cart_items)
        total = subtotal # shipping is 0
        
        return JsonResponse({
            'status': 'updated',
            'quantity': cart_item.quantity,
            'item_total': cart_item.product.price * cart_item.quantity,
            'subtotal': subtotal,
            'total': total,
            'cart_count': cart_items.count()
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def checkout_view(request):
    product_id = request.GET.get('product_id')
    
    if product_id:
        product = get_object_or_404(Product, id=product_id)
        if product.stock < 1:
            messages.error(request, f"Sorry, {product.name} is out of stock.")
            return redirect('product_detail', product_id=product.id)
            
        cart_items_data = [{
            'product': product,
            'quantity': 1,
            'total': product.price
        }]
        subtotal = product.price
    else:
        items = CartItem.objects.filter(user=request.user).select_related('product')
        if not items:
            messages.warning(request, "Your cart is empty.")
            return redirect('product_list')
        cart_items_data = [{ 
            'product': item.product, 
            'quantity': item.quantity, 
            'total': item.product.price * item.quantity
        } for item in items]
        subtotal = sum(item['total'] for item in cart_items_data)

    total = subtotal

    if request.method == 'POST':
        shipping_address = request.POST.get('address')
        payment_method = request.POST.get('payment', 'razorpay')
        
        if not shipping_address:
            messages.error(request, "Shipping address is required.")
            return redirect(f"{request.path}?product_id={product_id}" if product_id else request.path)

        # Handle Cash on Delivery
        if payment_method == 'cod':
            # Create order with COD payment method
            order = Order.objects.create(
                user=request.user,
                total_amount=total,
                shipping_address=shipping_address,
                payment_method='cod',
                payment_status='pending',
                is_paid=False
            )

            # Create order items
            for item in cart_items_data:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    price=item['product'].price
                )

            # Deduct stock and increment sales
            for item in cart_items_data:
                product = item['product']
                product.stock -= item['quantity']
                product.sales_count += item['quantity']
                product.save()

            # Clear cart if it was a cart checkout
            if not product_id:
                CartItem.objects.filter(user=request.user).delete()

            messages.success(request, "Order placed successfully! You will pay on delivery.")
            return redirect('thank_you')

        # Handle Online Payment (Razorpay)
        # Validate API keys first
        if (settings.RAZORPAY_KEY_ID == 'rzp_test_your_actual_key_here' or 
            settings.RAZORPAY_KEY_SECRET == 'your_actual_secret_here'):
            messages.error(request, 
                "Razorpay API keys not configured. Please run 'python setup_razorpay.py' to configure your API keys.")
            return redirect(f"{request.path}?product_id={product_id}" if product_id else request.path)
        
        try:
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            
            # Create Razorpay Order
            # amount is in paise (total * 100)
            razorpay_order = client.order.create({
                "amount": int(total * 100),
                "currency": "INR",
                "payment_capture": "1"
            })
            
            # Validate Razorpay response
            if not razorpay_order or 'id' not in razorpay_order:
                raise ValueError("Invalid Razorpay order response")
                
        except Exception as e:
            # Handle authentication or other API errors
            error_msg = "Payment gateway initialization failed. "
            if "Authentication failed" in str(e) or "BadRequestError" in str(type(e)):
                error_msg += "Please check your Razorpay API keys. Run 'python setup_razorpay.py' to reconfigure."
            elif "Invalid Razorpay order response" in str(e):
                error_msg += "Unable to create payment order. Please try again."
            else:
                error_msg += f"Error: {str(e)}"
            
            messages.error(request, error_msg)
            return redirect(f"{request.path}?product_id={product_id}" if product_id else request.path)

        # Create our database Order for online payment
        order = Order.objects.create(
            user=request.user,
            total_amount=total,
            shipping_address=shipping_address,
            payment_method='razorpay',
            payment_status='pending',
            razorpay_order_id=razorpay_order['id']
        )

        # Create order items
        for item in cart_items_data:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['product'].price
            )

        # Prepare context with validation
        context = {
            'order': order,
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_merchant_key': settings.RAZORPAY_KEY_ID,
            'razorpay_amount': razorpay_order['amount'],
            'currency': "INR",
            'user_email': request.user.email,
            'user_name': request.user.get_full_name() or request.user.username,
        }
        
        # Validate all required context variables
        required_keys = ['razorpay_order_id', 'razorpay_merchant_key', 'razorpay_amount', 'user_email', 'user_name']
        for key in required_keys:
            if not context.get(key):
                messages.error(request, f"Payment initialization error: Missing {key}")
                return redirect(f"{request.path}?product_id={product_id}" if product_id else request.path)
        
        return render(request, 'payment_processing.html', context)
        
    return render(request, 'checkout.html', {
        'cart_items': cart_items_data,
        'subtotal': subtotal,
        'total': total
    })

import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def verify_payment(request):
    if request.method == "POST":
        logger.info(f"Received payment verification request: {request.POST}")
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')

        if not all([razorpay_payment_id, razorpay_order_id, razorpay_signature]):
            messages.error(request, "Invalid payment response. Missing required fields.")
            logger.error("Invalid payment response. Missing required fields.")
            return redirect('cart')

        try:
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            
            # Verify the payment signature
            client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })

            # Get the payment details to verify amount
            payment_details = client.payment.fetch(razorpay_payment_id)
            logger.info(f"Payment details: {payment_details}")
            
            # Payment is successful, update order
            try:
                order = Order.objects.get(razorpay_order_id=razorpay_order_id)
            except Order.DoesNotExist:
                messages.error(request, "Order not found.")
                logger.error(f"Order not found for razorpay_order_id: {razorpay_order_id}")
                return redirect('cart')
            
            # Verify amount matches
            if int(payment_details['amount']) != int(order.total_amount * 100):
                messages.error(request, "Payment amount mismatch.")
                order.payment_status = 'cancelled'
                order.save()
                logger.error(f"Payment amount mismatch for order {order.id}. Expected {int(order.total_amount * 100)}, got {int(payment_details['amount'])}")
                return redirect('cart')

            # Check if payment was already processed
            if order.is_paid:
                messages.info(request, "This order has already been paid.")
                logger.warning(f"Order {order.id} has already been paid.")
                return redirect('thank_you')

            # Update order
            order.razorpay_payment_id = razorpay_payment_id
            order.razorpay_signature = razorpay_signature
            order.is_paid = True
            order.payment_status = 'completed'
            order.status = 'Pending'
            order.save()
            logger.info(f"Order {order.id} updated successfully.")

            # Deduct stock and increment sales for each item in the order
            for item in order.items.all():
                product = item.product
                if product.stock >= item.quantity:
                    product.stock -= item.quantity
                    product.sales_count += item.quantity
                    product.save()
                else:
                    # Stock issue - log it but don't fail the payment
                    messages.warning(request, f"Insufficient stock for {product.name}. Your order may be partially fulfilled.")
                    logger.warning(f"Insufficient stock for {product.name} in order {order.id}.")

            # Clear user's cart
            CartItem.objects.filter(user=order.user).delete()

            messages.success(request, "Payment successful! Your order has been placed.")
            return redirect('thank_you')

        except Exception as e:
            # Payment verification failed - log all exceptions
            logger.exception("Payment verification failed.")
            error_msg = "Payment verification failed"
            if isinstance(e, AssertionError):
                error_msg = "Payment signature verification failed. Payment may not be authentic."
            
            messages.error(request, error_msg)
            order = Order.objects.filter(razorpay_order_id=razorpay_order_id).first()
            if order:
                order.payment_status = 'failed'
                order.save()
            return redirect('cart')
    
    messages.error(request, "Invalid request method.")
    return redirect('cart')

@login_required
def payment_failed(request):
    razorpay_order_id = request.GET.get('order_id')
    
    if razorpay_order_id:
        try:
            order = Order.objects.get(razorpay_order_id=razorpay_order_id)
            order.payment_status = 'cancelled'
            order.save()
        except Order.DoesNotExist:
            pass
    
    messages.warning(request, "Payment was cancelled or failed. Please try again.")
    return redirect('checkout')

@login_required
def thank_you_view(request):
    return render(request, 'thank_you.html')

def add_to_cart(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'login_required'}, status=403)
        
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
        
        if not created:
            cart_item.quantity += 1
            cart_item.save()
            
        cart_count = CartItem.objects.filter(user=request.user).count()
        return JsonResponse({'status': 'added', 'cart_count': cart_count})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def get_cart_count(request):
    if not request.user.is_authenticated:
        return JsonResponse({'cart_count': 0, 'wishlist_count': 0})
    cart_count = CartItem.objects.filter(user=request.user).count()
    wishlist_count = Wishlist.objects.filter(user=request.user).count()
    return JsonResponse({'cart_count': cart_count, 'wishlist_count': wishlist_count})

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful.', extra_tags='auth')
            return redirect('index')
        else:
            # We don't add a message here because the tooltip handles password errors,
            # and individual field errors are shown below each field in the form.
            pass
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Check if user exists at all
        user_exists = User.objects.filter(username=username).exists()
        if not user_exists:
            messages.error(request, 'User not found. Please register first.', extra_tags='auth')
            return render(request, 'login.html')
            
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.info(request, f'You are now logged in as {username}.', extra_tags='auth')
            return redirect('index')
        else:
            messages.error(request, 'Invalid password. Please try again.', extra_tags='auth')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.info(request, 'You have successfully logged out.', extra_tags='auth')
    return redirect('index')

def password_reset_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        # Here we would normally trigger the actual password reset email logic
        # For now, as per the screenshots, we'll just redirect to the success page
        return redirect('password_reset_done')
    return render(request, 'password_reset.html')

from .decorators import superuser_required

@superuser_required
def admin_dashboard(request):
    products = Product.objects.all()
    return render(request, 'admin_dashboard.html', {'products': products})

@superuser_required
def admin_orders(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'admin_orders.html', {'orders': orders})

@superuser_required
def update_order_status(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        status = request.POST.get('status')
        if status in [s[0] for s in Order.STATUS_CHOICES]:
            order.status = status
            order.save()
            messages.success(request, f"Order {order.id} status updated to {status}.")
    return redirect('admin_orders')

@login_required
def my_account(request):
    orders = request.user.orders.all().order_by('-created_at')
    return render(request, 'my_account.html', {'orders': orders})

@superuser_required
def add_product(request):
    if request.method == 'POST':
        # Logic to handle form submission
        name = request.POST.get('name')
        category = request.POST.get('category')
        price = request.POST.get('price')
        description = request.POST.get('description')
        image_url = request.POST.get('image_url')
        gender = request.POST.get('gender')
        Product.objects.create(
            name=name, category=category, price=price, 
            description=description, image_url=image_url, gender=gender
        )
        messages.success(request, 'Product added successfully!')
        return redirect('admin_dashboard')
    return render(request, 'add_product.html')

@superuser_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.category = request.POST.get('category')
        product.price = request.POST.get('price')
        product.description = request.POST.get('description')
        product.image_url = request.POST.get('image_url')
        product.gender = request.POST.get('gender')
        product.save()
        messages.success(request, 'Product updated successfully!')
        return redirect('admin_dashboard')
    return render(request, 'edit_product.html', {'product': product})

@superuser_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, 'Product deleted successfully!')
    return redirect('admin_dashboard')

@superuser_required
def update_stock(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        try:
            quantity = int(request.POST.get('quantity', 0))
            if quantity >= 0:
                product.stock = quantity
                product.save()
                messages.success(request, f"Stock for {product.name} updated successfully!")
            else:
                messages.error(request, "Quantity must be a non-negative number.")
        except ValueError:
            messages.error(request, "Invalid quantity value.")
    return redirect('admin_dashboard')

@superuser_required
def admin_analysis(request):
    # Top 5 best selling products
    top_selling = Product.objects.all().order_by('-sales_count')[:5]
    
    # Products with low stock (< 20 units)
    low_stock = Product.objects.filter(stock__lt=20).order_by('stock')
    
    # All products for the detailed table
    all_products = Product.objects.all().order_by('name')
    
    # Data for charts
    top_selling_data = {
        'labels': [p.name for p in top_selling],
        'sales': [p.sales_count for p in top_selling]
    }
    
    low_stock_data = {
        'labels': [p.name for p in low_stock],
        'stock': [p.stock for p in low_stock]
    }

    context = {
        'top_selling': top_selling,
        'low_stock': low_stock,
        'all_products': all_products,
        'top_selling_data': top_selling_data,
        'low_stock_data': low_stock_data,
        'total_products': Product.objects.count(),
        'total_sales': sum(p.sales_count for p in Product.objects.all()),
        'out_of_stock': Product.objects.filter(stock=0).count()
    }
    return render(request, 'analysis.html', context)

def password_reset_done_view(request):
    return render(request, 'password_reset_done.html')
