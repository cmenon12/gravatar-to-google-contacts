import base64
import libgravatar
import requests
import logging
from constants import *
from typing import Union


class Gravatar(libgravatar.Gravatar):

    def __init__(self, email: str):
        self.logger = logging.getLogger(__name__)
        super(Gravatar, self).__init__(email)

    def download_image(self, rating: str = MAX_RATING) -> Union[bool, str]:

        # Get the URL of the image
        image_url = super(Gravatar, self).get_image(720, "404", False,
                                                    rating, True, True)
        logging.info("Gravatar URL calculated.")
        logging.debug("URL is " + image_url)

        try:
            # Download the image
            r = requests.get(image_url)
            r.raise_for_status()
            logging.info("Image successfully downloaded.")

            # Convert to base64 and return
            image_bytes = base64.b64encode(r.content)

            return image_bytes.decode("utf-8")

        # Catch any exception and don't return the raw response
        except requests.RequestException as e:
            logging.info(e)
            return False
