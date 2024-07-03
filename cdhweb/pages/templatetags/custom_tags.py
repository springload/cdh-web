import uuid

from django import template

from ..blocks.accordion_block import ProjectAccordion

register = template.Library()


@register.simple_tag(takes_context=True)
def unique_id(context, prefix="id-"):
    return f"{prefix}{uuid.uuid4().hex}"


@register.simple_tag
def get_accordion_heading_display(choice_value):
    choices_dict = dict(ProjectAccordion.AccordionTitles.choices)
    return choices_dict.get(choice_value)
