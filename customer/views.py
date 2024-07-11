from django.conf import settings
from django.shortcuts import render, redirect
from django.views import View
from.models import MenuItem, OrderModel
from django.db.models import Q
from django.core.mail import send_mail
# Create your views here.
class HomePage(View):
    def get(self, request):
        return render(request, template_name='customer/home.html')
    
class About(View):
    def get(self, request):
        return render(request, template_name='customer/about.html')
    
class Order(View):
    def get(self, request):
        snacks = MenuItem.objects.filter(category__name__contains='snack')
        soft_drinks = MenuItem.objects.filter(category__name__contains='soft')
        carbohydrates = MenuItem.objects.filter(category__name__contains='carbohydrates')
        proteins = MenuItem.objects.filter(category__name__contains='protein')
        vitamins = MenuItem.objects.filter(category__name__contains='vitamin')
        appetizers = MenuItem.objects.filter(category__name__contains='appetizers')
        dessert = MenuItem.objects.filter(category__name__contains='dessert')
        beverage_drinks = MenuItem.objects.filter(category__name__contains='beverage')
        context = {
            'snacks':snacks,
            'soft_drinks':soft_drinks,
            'carbohydrates':carbohydrates,
            'proteins':proteins,
            'vitamins':vitamins,
            'appetizers':appetizers,
            'dessert':dessert,
            'beverage_drinks':beverage_drinks
        }
        return render(request, template_name='customer/order.html', context=context)
    
    def post(self, request):
        first_name = request.POST.get('first_name')
        second_name = request.POST.get('second_name')
        email = request.POST.get('email')
        county = request.POST.get('county')
        sub_county = request.POST.get('sub_county')
        area = request.POST.get('area')
        order_items={
            'items': []
        }

        items = request.POST.getlist('items[]')
        for item in items:
            menu_item = MenuItem.objects.get(pk__contains=int(item))
            items_data = {
                'id': menu_item.pk,
                'name': menu_item.name,
                'price': menu_item.price
            }
            order_items['items'].append(items_data)
            price = 0
            item_ids = []

        for item in order_items['items']:
            price += item['price']
            item_ids.append(item['id'])
        order = OrderModel.objects.create(
            price=price,
            first_name=first_name,
            second_name=second_name,
            email=email,
            county=county,
            sub_county=sub_county,
            area=area
            )
        order.items.add(*item_ids)
        email_from = settings.EMAIL_HOST_USER
        body = ('Thank you for your order! Your food is been prepared and will be delivered soon\n '
                f'Your total: {price}\n'
                'Thank You again for the Order!')
        send_mail(
            subject='Thank you for the order', message=body, recipient_list=[email], fail_silently=False, from_email=email_from
        )
        context ={
            'items': order_items['items'],
            'price': price
        }
        return redirect(to='order_confirmation', pk=order.pk)
    

class Menu(View):
    def get(self, request):
        menu_items = MenuItem.objects.all()
        context = {
            'menu_items': menu_items
        }
        return render(request, template_name='customer/menu.html', context=context)
    
class Menu_search(View):
    def get(self, request):
        query = self.request.GET.get('q')
        menu_items = MenuItem.objects.filter(
            Q(name__icontains=query) |
            Q(price__icontains=query) |
            Q(description__icontains=query)
        )
        context = {
            'menu_items': menu_items
        }        
        return render(request, template_name='customer/menu.html', context=context)
    
class OrderConfirmation(View):
    def get(self, request, pk):
        order = OrderModel.objects.get(pk=pk)
        context = {
            'pk': order.pk,
            'items': order.items,
            'price': order.price
        }
        return render(request,template_name='customer/order_confirmation.html', context=context)        