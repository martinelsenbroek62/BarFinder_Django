import json

from prettyjson import PrettyJSONWidget


class PopularTimesWidget(PrettyJSONWidget):
    template_name = 'admin/widgets/populartimes.html'

    def get_context(self, name, value, attrs):
        context = {}
        object = json.loads(value)
        context['widget'] = {
            'name': name,
            'is_hidden': self.is_hidden,
            'required': self.is_required,
            'value': self.format_value(value),
            'attrs': self.build_attrs(self.attrs, attrs),
            'template_name': self.template_name,
            'object': object
        }
        return context
