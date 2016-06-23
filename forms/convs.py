from datetime import datetime

from . import exc


__all__ = [
    'Converter',
    'RawDict',
    'RawList',
    'Dict',
    'List',
    'Str',
    'Int',
    'Bool',
    'Date',
]


class Converter:
    raw_type = None

    def __init__(self, field):
        self.field = field

    def to_python(self, raw_value):
        if raw_value is None:
            return None
        if self.raw_type:
            if isinstance(raw_value, self.raw_type):
                return raw_value
            else:
                raise exc.RawValueTypeError(self.raw_type, self.field.name)
        else:
            return raw_value

    def from_python(self, value):
        if value is None:
            return None
        return value



class RawDict(Converter):
    raw_type = dict
    error_not_valid = 'Not a valid dict'


class RawList(Converter):
    raw_type = list
    error_not_valid = 'Not a valid list'


class Str(Converter):
    raw_type = str
    error_not_valid = 'Not a valid string'


class Int(Converter):
    raw_type = int
    error_not_valid = 'Not a valid integer'


class Bool(Converter):
    raw_type = bool
    error_not_valid = 'Not a valid boolean'


class Dict(Converter):
    raw_type = dict

    def to_python(self, raw_dict):
        raw_dict = super().to_python(raw_dict)
        if raw_dict is None:
            return None
        python_dict = {}
        errors = {}
        for subfield in self.field.fields:
            try:
                python_dict.update(subfield.to_python(raw_dict))
            except exc.ValidationError as e:
                errors.update(e.error)
        if errors:
            raise exc.ValidationError(errors)
        return python_dict

    def from_python(self, python_dict):
        python_dict = super().to_python(python_dict)
        if python_dict is None:
            return None
        raw_dict = {}
        for subfield in self.field.fields:
            raw_dict.update(subfield.from_python(python_dict))
        return raw_dict


class List(Converter):
    raw_type = list

    def __init__(self, field):
        super().__init__(field)
        assert len(field.fields)
        assert field.fields[0].name is None
        self.item_field = field.fields[0]

    def to_python(self, raw_list):
        raw_list = super().to_python(raw_list)
        if raw_list is None:
            return None
        python_list = []
        errors = []
        for raw_value in raw_list:
            try:
                python_value = self.item_field.to_python({None: raw_value})[None]
                python_list.append(python_value)
            except exc.ValidationError as e:
                errors.append(e.error[None])
            else:
                errors.append(None)
        if any(errors):
            raise exc.ValidationError(errors)
        return python_list

    def from_python(self, python_list):
        python_list = super().from_python(python_list)
        if python_list is None:
            return None
        return [self.item_field.from_python({None: value})[None] \
                for value in python_list]


class Date(Converter):
    raw_type = str
    error_not_valid = 'Not a valid date'

    def to_python(self, raw_value):
        value = super().to_python(raw_value)
        if value is None:
            return None
        try:
            return datetime.strptime(raw_value, self.field.format).date()
        except ValueError as e:
            raise exc.ValidationError(self.error_not_valid)

    def from_python(self, python_value):
        if python_value is None:
            return None
        return python_value.strftime(self.field.format)



