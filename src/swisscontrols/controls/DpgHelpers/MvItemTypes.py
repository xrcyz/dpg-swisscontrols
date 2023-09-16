from enum import Enum

class MvItemTypes(Enum):
    Button = 'mvAppItemType::mvButton'
    Text = 'mvAppItemType::mvText'
    ImageButton = 'mvAppItemType::mvImageButton'
    Checkbox = 'mvAppItemType::mvCheckbox'
    Window = 'mvAppItemType::mvWindowAppItem'
    # Add other item types as needed