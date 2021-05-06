from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from django.shortcuts import redirect
from django.utils import timezone
from .models import OrderItem, Order, BillingAddress
from home.models import Item
from .forms import CheckoutForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings


class CheckoutView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.filter(user=self.request.user, ordered=False).first()
        form = CheckoutForm()
        context = {
            'form': form,
            'object': order                  
        }
        return render(self.request, "checkout.html", context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_addres')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')
                # Functionality for those fields needs to be added
                #   same_shipping_address = form.cleaned_data.get(
                #       'same_shipping_address')
            #   save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')
                billing_address = BillingAddress.objects.filter(user=self.request.user).first()
                if not billing_address:
                    billing_address = BillingAddress(
                        user=self.request.user,
                        street_address=street_address,
                        apartment_address=apartment_address,
                        country=country,
                        zip=zip
                    )
                else:
                    billing_address.street_address = street_address
                    billing_address.apartment_address = apartment_address
                    billing_address.country = country
                    billing_address.zip = zip
                billing_address.save()
                order.billing_address = billing_address
                order.save()
                # TODO: add redirect to the selected paymnet option        
                return redirect('payment')
            print(form.errors)
            messages.warning(self.request, "Failed checkout")
            return redirect('checkout')
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("order-summary")


class PaymentView(View):
    def get(self, *args, **kwargs):
        return render(self.request, "payment.html")


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("/")


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "Item quantity was updated succesfully")
            return redirect("order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, "Item was added to your cart succesfully")
            return redirect("order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "Item was remove from cart succesfully")
        return redirect("order-summary")


def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            elif order_item.quantity == 1:
                order_item.delete()
            messages.info(request, "Item quantity was updated")
            return redirect("order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("product", slug=slug)


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request, "Item was removed from your cart sucesfully")
            return redirect("product", slug=slug)
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("product", slug=slug)


class SuccessView(View):
    def get(self, *args, **kwargs):
        session_id = self.request.GET.get('session_id')
        session = stripe.checkout.Session.retrieve(session_id)
        customer = stripe.Customer.retrieve(session.customer)
        order = Order.objects.get(user=self.request.user, ordered=False)
        order.ordered = True
        order.save()
        context = {
            'object': order,
            'customer_email': customer.email
        }
        return render(self.request, "success.html", context)


import os


import stripe
# This is your real test secret API key.
stripe.api_key = 'sk_test_51IUTHGAWMAUBj98U84CnKpfmV44EmBSxWGQAVeuwDr0ECfVlvdT9ImT3ZSdtfnRVtDwx6iCUxnEt0twSXu9lu1Th002CTlLLDB'


@csrf_exempt
def create_checkout_session(request):
    order = Order.objects.get(user=request.user, ordered=False)
    line_items = []
    for item in order.items.all():
        order_item = {
            'price_data': {
                'currency': 'usd',
                'unit_amount': int(item.item.price * 100),
                'product_data': {
                    'name': item.item.title,
                    'images': [request.build_absolute_uri(settings.MEDIA_URL + str(item.item.image))],
                },
            },
            'quantity': item.quantity,
        }
        line_items.append(order_item)
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,      
            mode='payment',
            success_url=settings.SITE_DOMAIN + '/checkout/success?session_id={CHECKOUT_SESSION_ID}', 
            cancel_url=settings.SITE_DOMAIN + '/cancel.html',
        )
        return JsonResponse({'id': checkout_session.id})
    except Exception as e:
        return JsonResponse({'error': str(e)})
