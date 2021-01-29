from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.http import HttpResponse
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Property, Photo, Plan, Feature, Client, Sale, Order

import csv
import datetime


def export_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    response = HttpResponse(content_type='application/csv')
    response['Content-Disposition'] = 'attachment;filename={}.csv'.format(opts.verbose_name_plural)

    writer = csv.writer(response)
    fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]
    writer.writerow([field.verbose_name for field in fields])

    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name, None)
            if isinstance(value, datetime.datetime):
                value = value.strftime('%d-%m-%Y')
            data_row.append(value)

        writer.writerow(data_row)

    return response


def receipt(obj):
    return mark_safe('<a href="{}">Receipt</a>'.format(reverse('realty:receipt', args=[obj.id])))


export_to_csv.short_description = 'Export to CSV'
receipt.short_description = 'Receipt'


# Register your models here.
class PlanInline(admin.TabularInline):
    model = Plan


class PhotoInline(admin.TabularInline):
    model = Photo


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('name', 'kind', 'type', 'scale', 'price', 'available')
    list_filter = ('kind', 'type', 'scale', 'date_created', 'date_updated', 'available')
    search_fields = ('name', 'address', 'description', 'feature__feature', 'price')
    date_hierarchy = 'date_created'
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('available', 'scale')
    # autocomplete_fields = ('feature',)
    inlines = [PlanInline, PhotoInline]


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('feature',)
    search_fields = ('feature',)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'email', 'telephone', 'occupation')
    list_filter = ('date',)
    search_fields = ('first_name', 'email', 'telephone', 'occupation', 'note')
    date_hierarchy = 'date'


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'sale_id', 'quantity', 'date_sold', receipt)
    list_filter = ('date_sold',)
    search_fields = ('sale_id', 'property__name', 'client__name', 'client__email')
    date_hierarchy = 'date_sold'
    autocomplete_fields = ('client', 'property')
    actions = [export_to_csv]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'first_name', 'last_name', 'phone', 'email', 'quantity')
    search_fields = ('order_id', 'first_name', 'last_name', 'phone', 'email', 'quantity')
    list_filter = ('date',)
    date_hierarchy = 'date'
    autocomplete_fields = ('property',)


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    date_hierarchy = 'action_time'
    list_filter = ('user', 'content_type', 'action_flag')
    search_fields = ('object_repr', 'change_message')
    list_display = ('action_time', 'user', 'content_type', 'action_flag')


admin.site.site_header = "Homebase Administration"
admin.site.index_title = "Homebase Admin"
admin.site.site_title = "Your Real Estate"
