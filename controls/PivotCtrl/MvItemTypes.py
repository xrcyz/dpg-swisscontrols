from enum import Enum

class MvItemTypes(Enum):
    Button = 'mvAppItemType::mvButton'
    Text = 'mvAppItemType::mvText'
    ImageButton = 'mvAppItemType::mvImageButton'
    Checkbox = 'mvAppItemType::mvCheckbox'
    # Add other item types as needed