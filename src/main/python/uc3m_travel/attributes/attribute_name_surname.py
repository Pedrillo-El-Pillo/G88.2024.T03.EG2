from uc3m_travel.attributes.attribute import Attribute

class NameSurname(Attribute):
    def __init__(self, attr_value):
        super().__init__()
        self._validation_pattern = r"^(?=^.{10,50}$)([a-zA-Z]+(\s[a-zA-Z]+)+)$"
        self._error_message = "Invalid name format"
        self._attr_value = self._validate(attr_value)