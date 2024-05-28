import uuid
from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def unique_id(context, prefix="id-"):
    return f"{prefix}{uuid.uuid4().hex}"
