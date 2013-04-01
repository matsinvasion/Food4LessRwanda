from .models import OrderItem
from restaurant_detail.models import Item
from django.shortcuts import get_object_or_404
import decimal
import random
from django.conf import settings
from django.contrib.auth.models import User



ORDER_ID_SESSION_KEY = 'shopping_id'

# get the current user's cart id, sets new one if blank
def _shopping_id(request):
	if request.session.get(ORDER_ID_SESSION_KEY,'') == '':
		request.session[ORDER_ID_SESSION_KEY] = _generate_shopping_id()
	return request.session[ORDER_ID_SESSION_KEY]
def _generate_shopping_id():
	shopping_id =''
	characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*()'
	order_id_length = 100
	for y in range(order_id_length):
		shopping_id += characters[random.randint(0,len(characters)-1
		)]
	return shopping_id
# return all items from the current user's order
def get_order_items(request):
	return OrderItem.objects.filter(shopping_id=_shopping_id(request))
# add an item to order
def add_to_order(request,obj): 	
	postdata = request.POST.copy()
	#get quantity added, return 0 if empty
	quantity = postdata.get('quantity',0)
	# fetch the item or return  missing page error_message
	i = get_object_or_404(Item,pk=obj.id)
#	order = get_object_or_404(Order,pk=obj.id)
	# get items in order
	order_items = get_order_items(request)
	item_in_orders = False
	# check to see if item is already in order
	for order_item in order_items:
		if order_item.item.id == i.id:
			#update the quantity if found
			order_item.augment_quantity(quantity)
			item_in_orders = True
	if not item_in_orders:
		# creat and save a new order item
		anon_user = User.objects.get(id=settings.ANONYMOUS_USER_ID)	
#		try:
#			customer = Customer.objects.get(pk=customer_id)
#			order= Order.objects.get(pk=order_id)
#			restaurant = Restaurant.objects.get(pk=restaurant_id)
#		except:
#			customer = Customer.objects.create(created_by=anon_user,modified_by=anon_user)
#			customer.save()
#			import pdb;pdb.set_trace()
#			restaurant = Restaurant(created_by=anon_user,modified_by=anon_user)
#			restaurant.save()
			
			
		oi=OrderItem.objects.create(shopping_id=_shopping_id(request),
		                                  quantity=quantity,
		                                  item=i,
		                                  created_by=anon_user,
		                                  modified_by=anon_user)
		oi.save()
	
						                                  
		                                  
	

		
# return the total number of items in the usser's cart
def order_distinct_item_count(request):
	return get_order_items(request).count()

def get_single_item(request,item_id):
	return get_object_or_404(OrderItem, id=item_id, shopping_id=_shopping_id(request))
# remove a single item from order
def remove_from_order(request):
	postdata = request.POST.copy()
	item_id = postdata['item_id']
	order_item = get_single_item(request, item_id)
	if order_item:
		order_item.delete()
# update quantity for single item_slug
def update_order(request):
	postdata = request.POST.copy()
	item_id = postdata['item_id']
	quantity = postdata['quantity']
	order_item = get_single_item(request, item_id)
	if order_item:
		if int(quantity) > 0:
			order_item.quantity = int(quantity)
			order_item.save()
		else:
			remove_from_order(request)
# gets the total for the current order
def order_subtotal(request,obj):		
	order_total = decimal.Decimal('0.00')
	order_items = get_order_items(request)
	for order_item in order_items:
		order_total += order_item.item.price * order_item.quantity
	return order_total
#def order_total(request):
#	order_total = decimal.Decimal('0.00')
#	order_item = get_order_items(request)
#	orders_subtotal = order_subtotal(request)
	
#	order_total += order_item.owner.service_fee + orders_subtotal
#	return order_total 

def is_empty(request):
	return order_distinct_item_count(request) == 0

def empty_cart(request):
	user_cart = get_order_items(request)
	user_cart.delete()
