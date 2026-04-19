from django import forms

from monitoring.models import Field, FieldUpdate, User


class DateInput(forms.DateInput):
    input_type = "date"


class FieldForm(forms.ModelForm):
    class Meta:
        model = Field
        fields = ["name", "crop_type", "planting_date", "current_stage", "assigned_agent"]
        widgets = {
            "planting_date": DateInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assigned_agent"].queryset = User.objects.filter(role=User.Role.FIELD_AGENT).order_by("first_name", "last_name", "username")
        self.fields["assigned_agent"].required = False
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "input")


class FieldStageUpdateForm(forms.ModelForm):
    class Meta:
        model = FieldUpdate
        fields = ["stage", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "input")
