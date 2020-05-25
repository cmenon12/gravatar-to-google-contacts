"""
A module that provides access to Gravatar APIs by extending libgravatar.
"""

import base64
import logging
from typing import Union

import libgravatar
import requests

# The max rating of the Gravatar
# One of g, pg, r, or x
MAX_RATING = "g"

# The resolution of the Gravatar that's downloaded (in px)
RESOLUTION = 720


class Gravatar(libgravatar.Gravatar):
    """
    This class facilitates access to the Gravatar API.

    This class extends the libgravatar.Gravatar class by providing an
    instance method to download an image.
    """

    def __init__(self, email: str):
        self.logger = logging.getLogger(__name__)
        super(Gravatar, self).__init__(email)

    def download_image(self, rating: str = MAX_RATING) -> Union[bool, str]:
        """
        Returns the image of the supplied Gravatar object.

        This method will download the image for the specified Gravatar
        and return it as a base64 string. It will return False on
        failure.
        :param rating: The maximum rating to accept (defaults to g,
        the lowest).
        :return: The image as a base64-encoded string, otherwise False
        on failure.
        """

        # Get the URL of the image
        image_url = super(Gravatar, self).get_image(RESOLUTION, "404", False,
                                                    rating, True, True)
        logging.info("Gravatar URL calculated.")
        logging.debug("URL is {}".format(image_url))

        try:
            # Download the image
            r = requests.get(image_url)
            r.raise_for_status()
            logging.info("Image successfully downloaded.")

            # Convert to base64 and return
            image_bytes = base64.b64encode(r.content)

            return image_bytes.decode("utf-8")

        # Catch any exception and don't return the raw response
        except requests.RequestException as err:
            logging.info(err)
            return False
