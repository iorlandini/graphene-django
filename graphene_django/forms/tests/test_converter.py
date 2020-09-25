from django import forms
from django.db import models
from py.test import raises

import graphene
from graphene import (
    String,
    Int,
    Boolean,
    Float,
    ID,
    UUID,
    List,
    NonNull,
    DateTime,
    Date,
    Time,
)

from ...types import DjangoObjectType
from ..converter import convert_form_field
from ..mutation import DjangoFormMutation


def assert_conversion(django_field, graphene_field, *args):
    field = django_field(*args, help_text="Custom Help Text")
    graphene_type = convert_form_field(field)
    assert isinstance(graphene_type, graphene_field)
    field = graphene_type.Field()
    assert field.description == "Custom Help Text"
    return field


def test_should_unknown_django_field_raise_exception():
    with raises(Exception) as excinfo:
        convert_form_field(None)
    assert "Don't know how to convert the Django form field" in str(excinfo.value)


def test_should_date_convert_date():
    assert_conversion(forms.DateField, Date)


def test_should_time_convert_time():
    assert_conversion(forms.TimeField, Time)


def test_should_date_time_convert_date_time():
    assert_conversion(forms.DateTimeField, DateTime)


def test_should_char_convert_string():
    assert_conversion(forms.CharField, String)


def test_should_email_convert_string():
    assert_conversion(forms.EmailField, String)


def test_should_slug_convert_string():
    assert_conversion(forms.SlugField, String)


def test_should_url_convert_string():
    assert_conversion(forms.URLField, String)


def test_should_choice_convert_string():
    assert_conversion(forms.ChoiceField, String)


def test_should_base_field_convert_string():
    assert_conversion(forms.Field, String)


def test_should_regex_convert_string():
    assert_conversion(forms.RegexField, String, "[0-9]+")


def test_should_uuid_convert_string():
    if hasattr(forms, "UUIDField"):
        assert_conversion(forms.UUIDField, UUID)


def test_should_integer_convert_int():
    assert_conversion(forms.IntegerField, Int)


def test_should_boolean_convert_boolean():
    field = assert_conversion(forms.BooleanField, Boolean)
    assert isinstance(field.type, NonNull)


def test_should_nullboolean_convert_boolean():
    field = assert_conversion(forms.NullBooleanField, Boolean)
    assert not isinstance(field.type, NonNull)


def test_should_float_convert_float():
    assert_conversion(forms.FloatField, Float)


def test_should_decimal_convert_float():
    assert_conversion(forms.DecimalField, Float)


def test_should_multiple_choice_convert_connectionorlist():
    field = forms.ModelMultipleChoiceField(queryset=None)
    graphene_type = convert_form_field(field)
    assert isinstance(graphene_type, List)
    assert graphene_type.of_type == ID


def test_should_manytoone_convert_connectionorlist():
    field = forms.ModelChoiceField(queryset=None)
    graphene_type = convert_form_field(field)
    assert isinstance(graphene_type, ID)


def test_form_field_with_choices_convert_enum():
    class TestModel(models.Model):
        field = models.CharField(
            choices=(("choice-0", "Choice 0"), ("choice-1", "Choice 1"))
        )

    class TestType(DjangoObjectType):
        class Meta:
            model = TestModel

    class TestForm(forms.ModelForm):
        class Meta:
            model = TestModel
            fields = ["field"]

    class TestMutation(DjangoFormMutation):
        class Meta:
            form_class = TestForm

    schema = graphene.Schema(mutation=TestMutation)

    _type = schema.get_type("TestModelField")
    assert _type.name == "TestModelField"

    assert _type.values[0].name == "CHOICE_0"
    assert _type.values[0].value == "choice-0"

    assert _type.values[1].name == "CHOICE_1"
    assert _type.values[1].value == "choice-1"
