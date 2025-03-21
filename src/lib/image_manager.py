import tkinter as tk
from typing import Dict, Tuple
from PIL import Image, ImageTk, ImageEnhance
from lib.types import Singleton
import debug
from lib import logger


PhotoImage = tk.PhotoImage | ImageTk.PhotoImage


class ImageManager(Singleton):
    image_cache: Dict[str, PhotoImage]

    def __init__(self):
        self.image_cache = {}

    def load(self, path: str, key: str | None=None, size: Tuple[int, int] | None=None) -> PhotoImage:
        if debug.VERBOSE:
            logger.log.info(f"loading image [{key}] = '{path}' with size {size}")
        
        if key is None:
            key = path

        if key not in self.image_cache:
            image = Image.open(str(path))

            brightness = 0.1
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(brightness)  

            if size:
                image = image.resize(size)
            image_tk = ImageTk.PhotoImage(image)
            self.image_cache[key] = image_tk

        return self.image_cache[key]

    def get(self, key: str) -> PhotoImage:
        if key not in self.image_cache:
            raise KeyError(key)
        return self.image_cache[key]


