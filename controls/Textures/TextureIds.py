from dataclasses import dataclass

@dataclass
class TexInfo:
    UUID: str
    PATH: str


class TextureIds:
    ID_PARTIAL_CHECK =  TexInfo(UUID='tx1', PATH='controls/assets/partial_check.png')
    # ID_TEX100 =  TexInfo(uuid='tx100', path='controls/assets/texture100.png')

    def __init__(self):
        raise RuntimeError("TextureIds should not be instantiated")

    @staticmethod
    def get_tex_info():
        ret = []
        for name in dir(TextureIds):
            if name.startswith('ID_'):
                value = getattr(TextureIds, name)
                # print(f"{name} = {value}")
                ret.append(value)
        return ret
