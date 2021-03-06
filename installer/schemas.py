from jsonschema import ValidationError, validate

from .inputs import get_json, get_yml


def _format_jsonschema_validation_error(e: ValidationError, name: str):
    """Converts an error raised by the jsonschema module into a custom string."""

    error_msg = ""
    if e.absolute_path and len(e.absolute_path) > 0:
        error_msg = f"'{'.'.join([str(x) for x in e.absolute_path])}': "

    return f"[{name}] " + error_msg + e.message


def validate_schema(name: str, data, schema):
    try:
        validate(data, schema)
    except ValidationError as e:
        raise ValidationError(_format_jsonschema_validation_error(e, name)) from None


def validate_config(name: str):
    data = get_yml(name)
    schema = get_json(name)
    validate_schema(name, data, schema)


def validate_all():
    for name in ["auths", "profiles", "services"]:
        validate_config(name)
