from django.contrib import admin
from .models import Plan, Subscription, Invoice

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'price', 'frequency', 'is_active')
    list_filter = ('frequency', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'price', 'frequency', 'is_active')
        }),
        ('Features', {
            'fields': ('post_limit', 'account_limit', 'team_members', 'analytics_access', 
                      'ai_generation', 'post_scheduling', 'calendar_view')
        }),
    )

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'plan')
    search_fields = ('user__email', 'payment_id')
    date_hierarchy = 'start_date'
    raw_id_fields = ('user', 'plan')

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'subscription', 'amount', 'status', 'invoice_date', 'due_date', 'paid_date')
    list_filter = ('status',)
    search_fields = ('subscription__user__email', 'transaction_id')
    date_hierarchy = 'invoice_date'
    raw_id_fields = ('subscription',) 