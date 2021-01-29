from django.db import models
from django.urls import reverse
from math import ceil
import string
import random

kind_choices = (('sale', 'for sale'), ('rent', 'for rent'), ('investment', 'for investment'))
type_choices = (('residential', 'residential'), ('commercial', 'commercial'), ('land', 'land'))
scale_choices = (
    ('unit', 'per unit'),
    ('year', 'per annum'),
    ('month', 'monthly'),
    ('week', 'weekly'),
    ('6-month', 'per 6-months'),
    ('plot', 'per plot'),
    ('acre', 'per acre'),
    ('hectare', 'per hectare'),
    ('none', 'nil')
)


# to generate eight value id
def random_number(character=8):
    letters = string.ascii_letters + string.digits
    choice_letter = ''.join(random.choice(letters) for _ in range(character))
    return choice_letter


# Create your models here.
class Feature(models.Model):
    feature = models.CharField(max_length=100)

    def __str__(self):
        return self.feature


class PropertyManager(models.Manager):
    def get_queryset(self):
        return super(PropertyManager, self).get_queryset().filter(available=True)


class Property(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=150, unique=True)
    kind = models.CharField(max_length=20, choices=kind_choices, default='investment')
    type = models.CharField(max_length=20, choices=type_choices, default='residential')
    scale = models.CharField(max_length=20, choices=scale_choices, default='none')
    description = models.TextField()
    feature = models.ManyToManyField(Feature, related_name='options')
    address = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    available = models.BooleanField(default=True)
    objects = models.Manager()
    opener = PropertyManager()

    class Meta:
        verbose_name_plural = 'Properties'

    def __str__(self):
        return self.name

    def get_features(self):
        items = self.feature.all()
        mid = ceil(len(items)/2)
        return [list(items[:mid]), list(items[mid:])]

    def get_absolute_url(self):
        return reverse('realty:property', args=[self.slug])


class Plan(models.Model):
    title = models.CharField(max_length=100)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='plans')
    image = models.ImageField(upload_to='property_plans')

    def __str__(self):
        return self.title


class Photo(models.Model):
    name = models.CharField(max_length=50)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='property_images')

    class Meta:
        verbose_name = 'Property Photo'
        verbose_name_plural = 'Property Photos'

    def __str__(self):
        return self.name


class Client(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    telephone = models.CharField(max_length=50, blank=True, null=True)
    occupation = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True, null=True)  # This in case you want to include some specific detail about client

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)


class Sale(models.Model):
    sale_id = models.CharField(max_length=8, default=random_number, unique=True)
    property = models.ForeignKey(Property, on_delete=models.SET_NULL, related_name='sales', null=True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, related_name='purchases', null=True)
    description = models.TextField(blank=True, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    date_created = models.DateTimeField(auto_now_add=True)
    date_sold = models.DateTimeField()

    def __str__(self):
        return self.sale_id

    def get_total_price(self):
        return self.quantity * self.property.price


class Order(models.Model):
    order_id = models.CharField(max_length=10, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField()
    property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.order_id

    def save(self, *args, **kwargs):
        self.order_id = random_number(5)
        super().save(*args, **kwargs)


