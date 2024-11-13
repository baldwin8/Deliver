from django.core.mail import send_mail
from django.shortcuts import render
from django.views import View
from .models import MenuItem, OrderModel
from django.conf import settings

class Order(View):
    def get(self, request, *args, **kwargs): 
        
        # Get every item from each category
        drinks = MenuItem.objects.filter(category__name__contains='drinks')
        lunch = MenuItem.objects.filter(category__name__contains='lunch')
        breakfast = MenuItem.objects.filter(category__name__contains='breakfast')
        
        # Pass into context
        context = {
            'lunch': lunch,
            'drinks': drinks,
            'breakfast': breakfast,
        }
        
        # Render the template
        return render(request, 'customer/order.html', context)
     
    def post(self, request, *args , **kwargs): 
        order_items = {  # Changed from Order_items to order_items
            'items': []
        }
        
        items = request.POST.getlist('items[]')
        
        for item in items:
            menu_item = MenuItem.objects.get(pk=int(item))  # pk is an exact match
            item_data = {
                'id': menu_item.pk,
                'name': menu_item.name,
                'price': menu_item.price
            }
            
            order_items['items'].append(item_data)
        
        price = 0
        item_ids = []
        
        # Calculate the total price and collect item ids
        for item in order_items['items']:
            price += item['price']
            item_ids.append(item['id'])
                
        # Create the order and add items to it
        order = OrderModel.objects.create(price=price)
        order.items.add(*item_ids)
        
        # Prepare context for confirmation page
        context = {
            'items': order_items['items'],
            'price': price
        }

        # Get the user's email (for simplicity, let's assume it's submitted via a form)
        user_email = request.POST.get('email')

        # Send confirmation email
        if user_email:
            self.send_order_confirmation_email(user_email, order_items['items'], price)

        # Render the order confirmation page
        return render(request, 'customer/order_confirmation.html', context)

    def send_order_confirmation_email(self, email, items, total_price):
        """Sends an email confirmation with the order details."""
        subject = 'Your Order Confirmation'
        message = 'Thank you for your order. Here is a summary:\n\n'

        # Construct the message with item details
        for item in items:
            message += f"{item['name']} - ${item['price']}\n"
        
        message += f"\nTotal Price: ${total_price}"

        # Send the email
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

class Index(View):
        def get(self, request, *args, **kwargs):
            
         return render(request, 'customer/index.html')           
                
class About(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'customer/about.html')            