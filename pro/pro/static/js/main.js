document.addEventListener('DOMContentLoaded', () => {
    // Navbar transparency effect on scroll
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.style.backgroundColor = 'rgba(255, 255, 255, 1)';
            navbar.style.padding = '15px 50px';
        } else {
            navbar.style.backgroundColor = 'rgba(255, 255, 255, 0.9)';
            navbar.style.padding = '20px 50px';
        }
    });

    // Fade-in animation for scroll elements
    const fadeElements = document.querySelectorAll('.product-item');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });

    fadeElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'all 0.6s ease-out';
        observer.observe(el);
    });

    // Hover effect for newsletter input
    const newsletterInput = document.querySelector('.newsletter input');
    const newsletterBtn = document.querySelector('.newsletter button');
    
    // AJAX CSRF Token setup
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    // Update global cart/wishlist counts
    const updateNavIcons = () => {
        fetch('/cart/count/')
            .then(res => res.json())
            .then(data => {
                const cartCount = document.getElementById('cart-count');
                const navHeart = document.getElementById('nav-wishlist-icon');
                
                if (cartCount && data.cart_count !== undefined) {
                    cartCount.innerText = data.cart_count;
                }
                
                if (navHeart && data.wishlist_count !== undefined) {
                    if (data.wishlist_count > 0) {
                        navHeart.classList.remove('far');
                        navHeart.classList.add('fas');
                        navHeart.style.color = '#e74c3c';
                    } else {
                        navHeart.classList.remove('fas');
                        navHeart.classList.add('far');
                        navHeart.style.color = 'inherit';
                    }
                }
            });
    };

    updateNavIcons();

    // Global add to cart function
    window.addToCart = (productId) => {
        fetch('/cart/add/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `product_id=${productId}`
        })
        .then(response => {
            if (response.status === 403) {
                window.location.href = '/login/';
                return;
            }
            return response.json();
        })
        .then(data => {
            if (data && data.status === 'added') {
                updateNavIcons();
                showToast();
            }
        });
    };

    // Toast Notification
    const showToast = () => {
        const toast = document.getElementById('toast-notification');
        toast.classList.add('show');
        setTimeout(() => {
            toast.classList.remove('show');
        }, 2500);
    };

    // Global toggle wishlist function
    window.toggleWishlist = (productId, btn) => {
        fetch('/wishlist/toggle/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `product_id=${productId}`
        })
        .then(response => {
            if (response.status === 403) {
                window.location.href = '/login/';
                return;
            }
            return response.json();
        })
        .then(data => {
            if (data && data.status === 'added') {
                btn.innerHTML = '<i class="fas fa-heart"></i>';
            } else if (data && data.status === 'removed') {
                btn.innerHTML = '<i class="far fa-heart"></i>';
            }
            updateNavIcons();
        });
    };
});
