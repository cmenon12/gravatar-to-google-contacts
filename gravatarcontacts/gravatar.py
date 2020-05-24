import base64
import libgravatar
import requests
import logging


class Gravatar(libgravatar.Gravatar):

    def __init__(self, email):
        self.logger = logging.getLogger(__name__)
        super(Gravatar, self).__init__(email)

    def download_image(self, rating="g"):

        # Get the URL of the image
        image_url = super(Gravatar, self).get_image(720, "404", False, rating, True, True)

        try:
            # Download the image
            r = requests.get(image_url)
            r.raise_for_status()

            # Convert to base64 and return
            image_bytes = base64.b64encode(r.content)
            return image_bytes.decode("utf-8")

        # Catch any exception and don't return the raw response
        except requests.RequestException as err:
            return False