from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.db.models import Q, Count
from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import render_to_string
from django.core.mail import EmailMessage, get_connection, send_mail
from django.conf import settings

from .models import Property, Sale
from blog.models import Post
from blog.views import subscribe
from homebase.settings import EMAIL_HOST_USER
from .forms import OrderForm

import csv
import weasyprint
from io import BytesIO
import os
import operator
from functools import reduce

choices = ('residential', 'commercial', 'land')
remove_word = ['in', 'a', 'an', 'the', 'of', 'to', 'for', 'with', 'at', 'either', 'and', 'or']

sales_backend = 'django.core.mail.backends.smtp.EmailBackend'
sales_email = os.getenv('HOST_USER')
sales_email_pwd = os.getenv('HOST_PASSWORD')
sales_port = 587
sales_host = 'tolufytech.com'


def contact_form(request):
    name = request.POST['name']
    email = request.POST['email']
    phone = request.POST['phone']
    message = request.POST['message']
    contact_info = [name, email, phone, message]
    if 'property' in request.POST:
        contact_info.append(request.POST['property'])

    with open('contact.csv', mode='a', newline='') as csv_object:
        csv_writer = csv.writer(csv_object, lineterminator='\n\n')
        csv_writer.writerow(contact_info)
    subject = 'Contact Message from ' + request.POST['email']
    recipient = ['lanre.toluwa@gmail.com']
    if 'property' in request.POST:
        email_message = 'Name: %s\nEmail: %s\nPhone: %s\nMessage: %s\nProperty: %s' % tuple(contact_info)
    else:
        email_message = 'Name: %s\nEmail: %s\nPhone: %s\nMessage: %s' % tuple(contact_info)
    send_mail(subject, email_message, EMAIL_HOST_USER, recipient, fail_silently=False)
    return messages.info(request, 'Thank you, %s for contacting us. We will get back to you as soon as possible' % name)


# for handling order requests
def order_form(request, property_object):
    new_order = OrderForm(request.POST)
    if new_order.is_valid():
        order = new_order.save(commit=False)
        order.property = property_object
        order.save()
        subject = 'Homebase Order'
        mail_realty = 'Property: {}\nName: {}\nEmail: {}\nPhone: {}\nQuantity: {}'\
            .format(order.property, order.first_name+' '+order.last_name, order.email, order.phone, order.quantity)
        order_notifier = ['tolufytech@gmail.com']  # realty email recipients of order

        send_mail(subject, mail_realty, EMAIL_HOST_USER, order_notifier, fail_silently=False)
        html_message = render_to_string('order-mail.html', {'order': order})
        mail_prospect = 'Hi, {}. We just received an order on {} from you.\nYour Order ID is {}\n\n' \
                        'We will contact you soon. Thanks!'.\
            format(order.first_name, order.property, order.order_id)
        order_mail_to = [order.email]
        send_mail('Homebase Order', mail_prospect, EMAIL_HOST_USER, order_mail_to, html_message=html_message,
                  fail_silently=False)
        if order.property.kind == 'sale':
            order_type = 'purchase'
        else:
            order_type = order.property.kind
        return 'Thank you, {}. Your {} order on {} was successful. We will contact you via the phone number or email ' \
               'address you provided.\nKindly check your email address for your order ID'.\
            format(order.first_name, order_type, order.property)


# view for the home page
def index(request):
    latest = Property.opener.all().order_by('-date_created')[:6]
    latest_blog = Post.publishee.all().order_by('publish')[:3]
    subscribe_alert = None
    if request.method == 'POST':
        if 'subscribe' in request.POST:
            subscribe_alert = subscribe(request)
        elif 'contact' in request.POST:
            contact_form(request)
    context = {
        'latest': latest,
        'latest_blog': latest_blog,
        'subscribe_alert': subscribe_alert,
    }
    return render(request, 'index.html', context)


# view for properties
def property_list(request, prop_type):
    if prop_type != 'properties':
        space = Property.opener.filter(type=prop_type).order_by('-date_created')
        if not space.exists():
            if prop_type not in choices:
                return HttpResponse('We think you must have missed where you\'re going.')
    else:
        space = Property.opener.all().order_by('-date_created')
    paginator = Paginator(space, 6)
    page = request.GET.get('page')

    try:
        pager = paginator.page(page)
    except PageNotAnInteger:
        pager = paginator.page(1)
    except EmptyPage:
        pager = paginator.page(paginator.num_pages)

    subscribe_alert = None
    if request.method == 'POST':
        if 'subscribe' in request.POST:
            subscribe_alert = subscribe(request)
    context = {
        'properties': pager,
        'prop_type': prop_type,
        'subscribe_alert': subscribe_alert,
    }
    return render(request, 'properties.html', context)


# view for each property
def detail(request, slug):
    main_object = Property.opener.get(slug=slug)
    subscribe_alert = None
    order_alert = None
    if request.method == 'POST':
        if 'subscribe' in request.POST:
            subscribe_alert = subscribe(request)
        elif 'contact' in request.POST:
            contact_form(request)
        elif 'order' in request.POST:
            order_alert = order_form(request, property_object=main_object)

    context = {
        'property': main_object,
        'subscribe_alert': subscribe_alert,
        'order_alert': order_alert,
    }
    return render(request, 'property.html', context)


# view for about us page
def about(request):
    subscribe_alert = None
    if request.method == 'POST':
        if 'subscribe' in request.POST:
            subscribe_alert = subscribe(request)
    context = {
        'subscribe_alert': subscribe_alert,
    }
    return render(request, 'about.html', context)


# view for contact us page
def contact(request):
    subscribe_alert = None
    if request.method == 'POST':
        if 'subscribe' in request.POST:
            subscribe_alert = subscribe(request)
        elif 'contact' in request.POST:
            contact_form(request)
    context = {
        'subscribe_alert': subscribe_alert,
    }

    return render(request, 'contact.html', context)


def search(request):
    main_search = request.GET.get('search')
    with open('search.csv', mode='a', newline='') as search_csv:
        search_writer = csv.writer(search_csv)
        search_writer.writerow([main_search])

    search_word = set(main_search.lower().split())
    search_word.difference_update(remove_word)  # removes words that are not keywords
    # print(f'search is {search_word}')

    property_query = [[Q(feature__feature__icontains=item), Q(description__icontains=item), Q(name__icontains=item),
                       Q(kind__icontains=item), Q(type__icontains=item), Q(price__icontains=item),
                       Q(address__icontains=item)] for item in search_word]

    property_query = [query for child in property_query for query in child]  # converts to 1 Dim list

    # query_map holds the model objects that satisfies the queries
    # query_dict holds unique objects in query_map and the number of times they appeared

    query_map = list(Property.objects.filter(i) for i in property_query)  # performs mass query and saves it in a list
    query_map = list(map(list, query_map))  # converts query sets in query_map to list
    query_map = [query for child in query_map for query in child]  # converts to query_map 1 Dim list

    query_dict = [[k, v] for k, v in dict.fromkeys(query_map).items()]  # converts query_map to dictionary
    query_times = list(map(query_map.count, [obj for obj, val in query_dict]))  # counts frequency of model objects

    for each in range(len(query_dict)):
        query_dict[each][1] = query_times[each]

    query_dict = sorted(query_dict, key=lambda b: b[1], reverse=True)
    # print(query_dict)

    # for blog
    post_query = [Q(title__icontains=item) for item in search_word]

    post_result = list(Post.objects.filter(i) for i in post_query)
    post_result = list(map(list, post_result))
    post_result = [query for child in post_result for query in child]

    post_dict = [[k, v] for k, v in dict.fromkeys(post_result).items()]
    post_times = list(map(post_result.count, [obj for obj, val in post_dict]))

    for each in range(len(post_dict)):
        post_dict[each][1] = post_times[each]

    post_dict = sorted(post_dict, key=lambda x: x[1], reverse=True)

    context = {
        'properties': query_dict,
        'posts': post_dict,
        'search': main_search,
    }

    return render(request, 'search.html', context)


# to view receipt
@staff_member_required
def receipt(request, obj_id):
    sale_object = Sale.objects.get(id=obj_id)
    context = {'sale': sale_object}
    return render(request, 'staff/sale-receipt.html', context)


# to send receipt to client
@staff_member_required
def send_receipt(request, obj_id):
    sale_object = Sale.objects.get(id=obj_id)
    context = {'sale': sale_object}
    if sale_object.property.kind == 'sale':
        transaction_type = 'purchase of '
    elif sale_object.property.kind == 'investment':
        transaction_type = 'investment on '
    else:
        transaction_type = sale_object.property.kind + ' of '

    subject = 'Homebase Receipt {} for {}'.format(sale_object.sale_id, transaction_type)
    message = 'Please, find attached the receipt for your recent {} {}'.\
        format(transaction_type, sale_object.property.name)
    mail_to = [sale_object.client.email]
    try:
        with get_connection(backend=sales_backend, host=sales_host, username=sales_email, password=sales_email_pwd, port=sales_port, use_tls=True) as connection:
            mail = EmailMessage(subject=subject, body=message, from_email=sales_email, to=mail_to, connection=connection)

        html = render_to_string('staff/receipt-mail.html', context)
        out = BytesIO()
        stylesheets = [weasyprint.CSS(os.path.join(settings.STATIC_ROOT, 'css', 'receipt.css'))]
        weasyprint.HTML(string=html).write_pdf(out, stylesheets=stylesheets)

        mail.attach('receipt_{}.pdf'.format(sale_object.sale_id), out.getvalue(), 'attachment/pdf')

        mail.send()
        messages.success(request, 'Receipt {} has been sent successfully'.format(sale_object.sale_id))
    except:
        messages.error(request, 'Receipt not sent. Check your internet connection or client\'s e-mail address')
    return render(request, 'staff/sale-receipt.html', context)


