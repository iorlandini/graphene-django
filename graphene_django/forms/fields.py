from django.forms import ChoiceField


class EnumField(ChoiceField):
    def __init__(self, enum, *args, **kwargs):
        self.enum = enum
        super().__init__(*args, **kwargs)
