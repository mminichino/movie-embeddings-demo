##
##

from moviedemo.restmgr import RESTManager
from PIL import Image
from typing import Union
import io
import PIL


class CheckImage:

    def __init__(self):
        pass

    @staticmethod
    def check_image_bytes(image_bytes: bytes) -> Union[str, None]:
        try:
            img = Image.open(io.BytesIO(image_bytes))
            return img.format
        except PIL.UnidentifiedImageError:
            return None

    def check_image_url(self, image_url: str) -> Union[str, None]:
        image_bytes = RESTManager().get_url_content(image_url)
        return self.check_image_bytes(image_bytes)
