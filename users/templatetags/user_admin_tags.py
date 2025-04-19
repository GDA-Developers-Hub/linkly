from django import template

register = template.Library()

@register.filter
def platform_color(counter):
    colors = [
        '#4267B2',  # Facebook blue
        '#E1306C',  # Instagram pink
        '#0077B5',  # LinkedIn blue
        '#FF0000',  # YouTube red
        '#000000',  # TikTok black
        '#0088CC',  # Telegram blue
    ]
    return colors[(counter - 1) % len(colors)] 