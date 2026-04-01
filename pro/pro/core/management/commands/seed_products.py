from django.core.management.base import BaseCommand
from core.models import Product

class Command(BaseCommand):
    help = 'Seeds the database with 15 initial products'

    def handle(self, *args, **kwargs):
        products = [
            {'name': 'Steel Bracelet Alpha', 'category': 'Steel', 'price': 1499, 'image_url': 'https://images.unsplash.com/photo-1611085583191-a3b13b944421?auto=format&fit=crop&q=80&w=400', 'description': 'A bold and elegant steel bracelet for the modern man.'},
            {'name': 'Steel Ring Titan', 'category': 'Steel', 'price': 999, 'image_url': 'https://images.unsplash.com/photo-1605100804763-247f67b3557e?auto=format&fit=crop&q=80&w=400', 'description': 'A titan among rings, crafted from high-grade stainless steel.'},
            {'name': 'Stone Pendant Nova', 'category': 'Stone', 'price': 1299, 'image_url': 'https://images.unsplash.com/photo-1573408301185-9146fe634ad0?auto=format&fit=crop&q=80&w=400', 'description': 'A celestial stone pendant that shines with natural beauty.'},
            {'name': 'Steel Chain Orion', 'category': 'Steel', 'price': 1799, 'image_url': 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&q=80&w=400', 'description': 'A robust and stylish steel chain, perfect for everyday wear.'},
            {'name': 'Stone Bead Bracelet Terra', 'category': 'Stone', 'price': 899, 'image_url': 'https://images.unsplash.com/photo-1535303311164-664fc9ec6532?auto=format&fit=crop&q=80&w=400', 'description': 'Earth-toned stone beads for a grounded and natural look.'},
            {'name': 'Steel Cuff Ares', 'category': 'Steel', 'price': 1599, 'image_url': 'https://images.unsplash.com/photo-1611591437281-460bfbe1220a?auto=format&fit=crop&q=80&w=400', 'description': 'A warrior-inspired steel cuff, strong and commanding.'},
            {'name': 'Stone Ring Gaia', 'category': 'Stone', 'price': 1099, 'image_url': 'https://images.unsplash.com/photo-1617038260897-41a1f14a8ca0?auto=format&fit=crop&q=80&w=400', 'description': 'A tribute to nature, this stone ring is uniquely beautiful.'},
            {'name': 'Steel Pendant Helios', 'category': 'Steel', 'price': 1399, 'image_url': 'https://images.unsplash.com/photo-1601121141461-9d6647bca1ed?auto=format&fit=crop&q=80&w=400', 'description': 'Radiate confidence with this sun-inspired steel pendant.'},
            {'name': 'Stone Necklace Luna', 'category': 'Stone', 'price': 1499, 'image_url': 'https://images.unsplash.com/photo-1599643477877-530eb83ba8e8?auto=format&fit=crop&q=80&w=400', 'description': 'A moon-inspired stone necklace for an elegant evening look.'},
            {'name': 'Steel Studs Volt', 'category': 'Steel', 'price': 799, 'image_url': 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&q=80&w=400', 'description': 'Electrifying steel studs that add a spark to your style.'},
            {'name': 'Stone Charm Echo', 'category': 'Stone', 'price': 699, 'image_url': 'https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?auto=format&fit=crop&q=80&w=400', 'description': 'A subtle yet meaningful stone charm, an echo of nature.'},
            {'name': 'Steel Bangle Draco', 'category': 'Steel', 'price': 1699, 'image_url': 'https://images.unsplash.com/photo-1576053139778-7e32f2ae3cfd?auto=format&fit=crop&q=80&w=400', 'description': 'A dragon-inspired steel bangle, sleek and powerful.'},
            {'name': 'Stone Earrings Aurora', 'category': 'Stone', 'price': 1899, 'image_url': 'https://images.unsplash.com/photo-1635767798638-3e25273a8236?auto=format&fit=crop&q=80&w=400', 'description': 'Stone earrings that glow with the colors of the aurora.'},
            {'name': 'Steel Signet King', 'category': 'Steel', 'price': 2499, 'image_url': 'https://images.unsplash.com/photo-1611085583191-a3b13b944421?auto=format&fit=crop&q=80&w=400', 'description': 'A regal steel signet ring, fit for a king.'},
            {'name': 'Stone Mala Zen', 'category': 'Stone', 'price': 3499, 'image_url': 'https://images.unsplash.com/photo-1573408301185-9146fe634ad0?auto=format&fit=crop&q=80&w=400', 'description': 'A peaceful stone mala for mindfulness and spiritual style.'},
        ]

        for p_data in products:
            Product.objects.update_or_create(
                name=p_data['name'],
                defaults={
                    'category': p_data['category'],
                    'price': p_data['price'],
                    'image_url': p_data['image_url'],
                    'description': p_data['description'],
                    'gender': 'Men'
                }
            )
        self.stdout.write(self.style.SUCCESS('Successfully seeded 15 products'))
