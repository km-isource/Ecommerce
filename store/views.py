from django.shortcuts import render, redirect, HttpResponseRedirect, get_object_or_404
from django.contrib.auth.hashers import check_password, make_password
from django.views import View
from .models import Category, Customer, Products, Order
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

class Index(View):
    def post(self, request):
        product_id = request.POST.get('product')
        remove = request.POST.get('remove')
        cart = request.session.get('cart', {})

        if cart:
            quantity = cart.get(product_id)
            if quantity:
                if remove:
                    if quantity <= 1:
                        cart.pop(product_id)
                    else:
                        cart[product_id] = quantity - 1
                else:
                    cart[product_id] = quantity + 1
            else:
                cart[product_id] = 1
        else:
            cart = {product_id: 1}

        request.session['cart'] = cart
        return redirect('homepage')


    def get(self, request):
        return HttpResponseRedirect(f'/store{request.get_full_path()[1:]}')

def store(request):
    cart = request.session.get('cart')
    if not cart:
        request.session['cart'] = {}
    products = None
    categories = Category.get_all_categories() 
    categoryID = request.GET.get('category')
    if categoryID:
        products = Products.get_all_products_by_categoryid(categoryID)
    else:
        products = Products.get_all_products()
        
    data = {'products': products, 'categories': categories, 'cart': cart}
    return render(request, 'index.html', data)

class Login(View):
    return_url = None
    
    def get(self, request):
        Login.return_url = request.GET.get('return_url')
        return render(request, 'login.html')
    
    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        customer = Customer.get_customer_by_email(email)
        error_message = None
        if customer:
            flag = check_password(password, customer.password)
            if flag:
                request.session['customer'] = customer.id
                if Login.return_url:
                    return HttpResponseRedirect(Login.return_url)
                else:
                    Login.return_url = None
                    return redirect('homepage')
            else:
                error_message = "Invalid Password"
        else:
            error_message = "Invalid Email"
        
        return render(request, 'login.html', {'error': error_message})

def logout(request):
    request.session.clear()
    return redirect('login')

class Signup(View):
    def get(self, request):
        return render(request, 'signup.html')
    
    def post(self, request):
        postData = request.POST
        first_name = postData.get('first_name')
        last_name = postData.get('last_name')
        phone = postData.get('phone')
        email = postData.get('email')
        password = postData.get('password')
        
        value = {
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone,
            'email': email
        }
        
        error_message = None
        customer = Customer(first_name=first_name,
                            last_name=last_name,
                            phone=phone,
                            email=email,
                            password=password)
        error_message = self.validateCustomer(customer)
        
        if not error_message:
            customer.password = make_password(customer.password)
            customer.register()
            return redirect('homepage')
        else:
            data = {'error': error_message, 'values': value}
            return render(request, 'signup.html', data)
    
    def validateCustomer(self, customer):
        error_message = None
        if not customer.first_name:
            error_message = "First Name is required"
        elif len(customer.first_name) < 3:
            error_message = "First Name must be at least 3 characters"
        elif not customer.last_name:
            error_message = "Last Name is required"
        elif len(customer.last_name) < 3:
            error_message = "Last Name must be at least 3 characters"
        elif not customer.phone:
            error_message = "Phone is required"
        elif len(customer.phone) < 10:
            error_message = "Phone must be at least 10 characters"
        elif not customer.email:
            error_message = "Email is required"
        elif len(customer.email) < 6:
            error_message = "Email must be at least 6 characters"
        elif not customer.password:
            error_message = "Password is required"
        elif len(customer.password) < 6:
            error_message = "Password must be at least 6 characters"
        elif customer.isExists():
            error_message = "Email already exists"
        return error_message

class Checkout(View):
    @login_required
    def get(self, request):
        # Make sure to check for cart in session
        cart = request.session.get('cart', {})
        if not cart:
            return redirect('store')  # Redirect if no items in cart

        # Access the logged-in user directly via request.user
        user = request.user

        # Ensure the user has an associated Customer object
        try:
            customer = Customer.objects.get(user=user)
        except Customer.DoesNotExist:
            return redirect('profile')  # Redirect to profile page if no customer exists for the user

        # Get the products in the cart based on the product IDs
        products = Products.get_products_by_id(list(cart.keys()))

        # Render checkout page with the products in the cart
        return render(request, 'checkout.html', {'products': products})

    @login_required
    def post(self, request):
        # Same cart check in the POST method
        cart = request.session.get('cart', {})
        if not cart:
            return redirect('store')

        # Get the address and phone from the form
        address = request.POST.get('address')
        phone = request.POST.get('phone')

        # Access the logged-in user directly via request.user
        user = request.user

        # Ensure the user has an associated Customer object
        try:
            customer = Customer.objects.get(user=user)
        except Customer.DoesNotExist:
            return redirect('profile')  # Redirect to profile if no customer exists

        # Process the order
        products = Products.get_products_by_id(list(cart.keys()))

        for product in products:
            order = Order(
                customer=customer,
                product=product,
                price=product.price,
                address=address,
                phone=phone,
                quantity=cart.get(str(product.id), 0)
            )
            order.save()

        # Clear the cart after placing the order
        request.session['cart'] = {}

        # Redirect to cart (or success page)
        return redirect('cart')  # Redirect to the cart or any other relevant page

class OrderView(View):
    @login_required
    def get(self, request):
        customer = request.session.get('customer')
        orders = Order.get_orders_by_customer(customer)
        return render(request, 'orders.html', {'orders': orders})

class Cart(View):
    def get(self, request):
        cart = request.session.get('cart', {})
        if not cart:
            cart = {}
            
        product_ids = [int(product_id) for product_id in cart.keys()]
        print(f"Cart IDs: {product_ids}")
        
        products = Products.get_products_by_id(list(cart.keys()))
        
        print(f"Products: {products}")

        cart_items = []
        total_price = 0
        for product in products:
            quantity = cart.get(str(product.id), 0)
            product_total = product.price * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total': product_total
            })
            total_price += product_total

        return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})

    def post(self, request):
        product_id = request.POST.get('product_id')
        action = request.POST.get('action')
        
        print(f"Product ID: {product_id}, Action: {action}")
        
        if not product_id or not action:
            return redirect('cart')
    
        product_id = str(product_id)
        cart = request.session.get('cart', {})

        if action == 'remove':
            if product_id in cart:
                del cart[product_id]
        elif action == 'update':
            quantity = int(request.POST.get('quantity', 1))
            if quantity > 0:
                cart[product_id] = quantity
            else:
                if product_id in cart:
                    del cart[product_id]
        elif action == 'add':
            quantity = int(request.POST.get('quantity', 1))
            cart[product_id] = cart.get(product_id, 0) + quantity
        
        print(f"Updated Cart: {cart}")

        request.session['cart'] = cart
        return redirect('cart')

def products_by_category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    products = Products.objects.filter(category=category)
    
    context = {
        'category': category,
        'products': products
    }
    
    return render(request, 'products_by_category.html', context)


def product_detail(request, product_slug):
    product = get_object_or_404(Products, slug=product_slug)
    
    context = {
        'product': product
    }
    return render(request, 'product_detail.html', context)

