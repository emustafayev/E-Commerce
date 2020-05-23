from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from core.forms import CheckoutForm, CouponForm, PaymentForm
from .models import Item, Order, OrderItem, Address, Coupon
from core.models import Payment as PaymentModel
import random
import string



# Need to fix
	#Problem adding non-existed coupon
	#direct access to payment view
	#...	


def home_view(request):
	context = {
		'items':Item.objects.all()
	}
	return render(request,"home.html",context)

class HomeView(ListView):
	model = Item
	paginated_by = 10
	template_name = "home.html"

class ItemDetailedView(DetailView):
	model=Item
	template_name="product.html"

@login_required
def add_to_cart(request,slug):
	item = get_object_or_404(Item,slug=slug)
	order_item, created = OrderItem.objects.get_or_create(  #return two param created or not and object
		item=item,
		user=request.user,
		ordered=False
		)
	current_orders = Order.objects.filter(user = request.user,ordered=False)
	if current_orders.exists():
		order = current_orders[0]
		#if order item is in order
		if order.items.filter(item__slug=slug).exists():
			order_item.quantity += 1
			order_item.save()
			messages.info(request,"This item quantity updated")
			return redirect('core:order-summary')
		else:
			order.items.add(order_item)
			messages.info(request, "This item was added to your cart.")
			return redirect('core:order-summary')
	else:
		ordered_date = timezone.now()
		order = Order.objects.create(
			user = request.user, ordered_date=ordered_date)
		order.items.add(order_item)
		order.save()
		messages.info(request, "This item was added to your cart.")
		return redirect('core:order-summary')

@login_required
def remove_from_cart(request,slug):
	item = get_object_or_404(Item,slug=slug)
	currentOrder = Order.objects.filter(user=request.user,ordered=False)

	if currentOrder.exists():
		order = currentOrder[0]
		if order.items.filter(item__slug=slug).exists():
			order_item = OrderItem.objects.filter(
				item=item,
				user=request.user,
				ordered=False)[0]
			order_item.quantity=1
			order_item.save()
			order.items.remove(order_item)
			messages.info(request,"Item removed from your chart!")
			return redirect('core:home')  # Further implementation redirect to order summary 
		else:
			messages.info(request, "This item was not in your cart")
			return redirect('core:home')  # Further implementation redirect to order summary 
	else:
		messages.info(request,"You dont have active order!")
		return redirect('core:home')

class OrderSummary(LoginRequiredMixin,View):
	def get(self, *args, **kwargs):
		try:
			order = Order.objects.get(user=self.request.user, ordered=False)
			context = {
				'object': order
			}
			return render(self.request, 'order_summary.html', context)
		except ObjectDoesNotExist:
			messages.warning(self.request, "You do not have an active order")
			return redirect('core:home')

@login_required
def remove_single_item_from_cart(request,slug):
	item = get_object_or_404(Item,slug=slug)
	order_item = OrderItem.objects.get_or_create(
		item=item,
		user=request.user,
		ordered=False)[0]
	order_qs = Order.objects.filter(user = request.user, ordered=False)
	if order_qs.exists():
		order = order_qs[0]
		if order.items.filter(item__slug=slug).exists():
			if order_item.quantity > 1:
				order_item.quantity -= 1
				order_item.save()
			else:
				order_item.quantity=0
				order.items.remove(order_item)
				order.save()
			messages.info(request,'Item Value updated!')
			return redirect('core:order-summary')
		else:
			messages.info(request,"Item is not in your cart!")
			return redirect('core:order-summary')
	else:
		messages.info(request,"You dont have a active order!")
		return redirect('core:order-summary') 

def is_valid_form(values):
	valid = True
	for field in values:
		if field == '':
			valid = False
	return valid

class CheckoutView(LoginRequiredMixin,View):
	def get(self,*args,**kwargs):
		try:
			order = Order.objects.get(user=self.request.user,ordered=False)
			form = CheckoutForm()
			conext = {
				'form':form,
				'couponform':CouponForm(),
				'order':order,
				'DISPLAY_COUPON_FORM':True
			}

			shipping_address = Address.objects.filter(user=self.request.user)
			if shipping_address.exists():
				conext.update(
					{'default_shipping_address':shipping_address[0]}
					)
			
			return render(self.request,"checkout.html",conext)

		except ObjectDoesNotExist:
			messages.info(self.request,"You dont have active order!")
			return redirect('core:home')

	def post(self,*args,**kwargs):
		form = CheckoutForm(self.request.POST or None)
		try:
			order_qs = Order.objects.filter(user = self.request.user, ordered=False)
			if form.is_valid():
				order = order_qs[0]
				use_default_shipping = form.cleaned_data.get(
					'use_default_shipping')
				if use_default_shipping:
					default_shipping = Address.objects.filter(user=self.request.user,default=True)
					if default_shipping.exists():
						address = default_shipping[0]
						order.shipping_address=address
						order.save
					else:
						messages.warning(self.request,"You dont have default shipping address")
						return redirect('core:checkout')
				else:
					print("User is entering a new shipping address")
					shipping_address1 = form.cleaned_data.get(
                        'shipping_address')
					shipping_address2 = form.cleaned_data.get(
                        'shipping_address2')
					shipping_country = form.cleaned_data.get(
                        'shipping_country')
					shipping_zip = form.cleaned_data.get('shipping_zip')
					
					if is_valid_form([shipping_address1,shipping_address2,shipping_country,shipping_zip]):
						shipping_address = Address(
                            user=self.request.user,
                            street_address=shipping_address1,
                            apartment_address=shipping_address2,
                            country=shipping_country,
                            zip=shipping_zip,
						)

						shipping_address.save()
						order.shipping_address=shipping_address
						order.save()

						set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')
						set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')
						if set_default_shipping:
							shipping_address.default=True
							shipping_address.save()
							print("I came here too!")
						print("I came here!")
						return redirect('core:payment')
					else:
						messages.warning(self.request,"Fill required fields correctly!")				
						return redirect('core:checkout')
				return redirect('core:payment') #success
				#Shoudld return HTTP Response
			else:
				messages.warning(self.request,"Fill required fields correctly!")				
				return redirect('core:checkout')
		except ObjectDoesNotExist:	
			messages.info(self.request,"You dont have active order!")
			return redirect('core:home')

def get_coupon(request,code):
	try:
		coupon = Coupon.objects.get(code=code)
		return coupon
	except ObjectDoesNotExist:
		messages.warning(request,"Can't find specified coupon!")
		return redirect('core:checkout')



class AddCouponView(View):
	def post(self,*args,**kwargs):
		form = CouponForm(self.request.POST or None)
		if form.is_valid():
			code = form.cleaned_data.get('code')
			order = Order.objects.filter(user=self.request.user,ordered=False)[0]
			coupon = get_coupon(self.request,code)
			order.coupon = coupon 
			order.save()
			messages.info(self.request,"Coupon added successfully!")
			return redirect('core:checkout')

def generateChargeID():
	return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

class Payment(LoginRequiredMixin,View):
	def get(self,*args,**kwargs):
		order_qs = Order.objects.filter(user = self.request.user, ordered=False)
		if order_qs.exists():
			order = order_qs[0]
			total_amount = order.get_total()
			context = {
				'order':order,
				'DISPLAY_COUPON_FORM':False
			}
			return render(self.request,"payment.html",context)
		else:
			messages.info(self.request,"You dont have active order!")
			return redirect('core:home')

	def post(self,*args, **kwargs):
		form = PaymentForm(self.request.POST or None)
		try:
			order = Order.objects.filter(user=self.request.user,ordered=False)[0]			
			if form.is_valid():
				order.ordered=True
				payment = PaymentModel.objects.create(user = self.request.user,
				 stripe_charge_id=generateChargeID(),
				 amount=order.get_total()
				 )
				token = form.cleaned_data.get('stripeToken')
				print(token)
				payment.save()
				order.payment=payment
				order.items.quantity=1
				order.save()
				messages.SUCCESS
				return redirect('core:home')
			else:
				messages.warning(self.request,"Fill fields correctly!")
				return redirect('core:payment')
		except ObjectDoesNotExist:
			messages.info(self.request,"You dont have active order!")
			return redirect('core:home')
