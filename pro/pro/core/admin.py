from django.contrib import admin
from .models import Product, CartItem, Wishlist, Order, OrderItem, Review

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'sales_count', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__username', 'product__name')

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__username', 'product__name')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('price',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'payment_method', 'payment_status', 'status', 'created_at')
    list_filter = ('payment_method', 'payment_status', 'status', 'created_at')
    search_fields = ('user__username', 'user__email', 'shipping_address')
    readonly_fields = ('id', 'created_at', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature')
    inlines = [OrderItemInline]
    fieldsets = (
        ('Order Information', {
            'fields': ('id', 'user', 'created_at', 'total_amount', 'shipping_address', 'status')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'payment_status', 'is_paid', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature')
        }),
    )

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'product__name', 'comment')
