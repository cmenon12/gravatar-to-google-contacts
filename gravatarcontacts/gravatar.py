"""
A module that provides access to Gravatar APIs by extending libgravatar.
"""

import base64
import logging
from typing import Union

import libgravatar
import requests

__author__ = "Christopher Menon"
__credits__ = ["Christopher Menon",
               "https://github.com/pabluk/libgravatar"]
__license__ = "gpl-3.0"

# The max rating of the Gravatar
# One of g, pg, r, or x
MAX_RATING = "g"

# The resolution of the Gravatar that's downloaded (in px)
RESOLUTION = 720

LOGGER = logging.getLogger(__name__)


class Gravatar(libgravatar.Gravatar):
    """
    Dacilitates access to the Gravatar API.

    This class extends the libgravatar.Gravatar class by providing an
    instance method to download an image.
    """

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
        LOGGER.info("Gravatar URL calculated.")
        LOGGER.debug("URL is %s", image_url)

        try:
            # Download the image
            r = requests.get(image_url)
            r.raise_for_status()
            LOGGER.info("Image successfully downloaded.")

            # Convert to base64 and return
            image_bytes = base64.b64encode(r.content)
            image_str = image_bytes.decode("utf-8")
            assert isinstance(image_str, str)

            return image_str

        # Catch any exception and don't return the raw response
        except requests.RequestException as err:
            LOGGER.info(err)
            return False
