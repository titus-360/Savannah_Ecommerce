from django import template

register = template.Library()

@register.filter
def status_color(status):
    """Return the appropriate Bootstrap color class for the order status"""
    status_colors = {
        'pending': 'warning',
        'processing': 'info',
        'shipped': 'primary',
        'delivered': 'success',
        'cancelled': 'danger'
    }
    return status_colors.get(status, 'secondary')
