from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('products/', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('product/<int:product_id>/review/', views.submit_review, name='submit_review'),
    path('my-account/', views.my_account, name='my_account'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password-reset/', views.password_reset_view, name='password_reset'),
    path('password-reset/done/', views.password_reset_done_view, name='password_reset_done'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/', views.toggle_wishlist, name='toggle_wishlist'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/update/', views.update_cart_quantity, name='update_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('payment/verify/', views.verify_payment, name='verify_payment'),
    path('payment/failed/', views.payment_failed, name='payment_failed'),
    path('thank-you/', views.thank_you_view, name='thank_you'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/count/', views.get_cart_count, name='get_cart_count'),

    # Admin
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/add/', views.add_product, name='add_product'),
    path('admin-dashboard/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('admin-dashboard/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('admin-dashboard/update-stock/<int:product_id>/', views.update_stock, name='update_stock'),
    path('admin-dashboard/analysis/', views.admin_analysis, name='admin_analysis'),
    path('admin-dashboard/orders/', views.admin_orders, name='admin_orders'),
    path('admin-dashboard/orders/update-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
]
