import libgravatar as libgravatar
import requests
import logging

from gravatar_to_contacts import DEFAULT_IMAGE_SIZE


class Gravatar(libgravatar.Gravatar) :

    def __init__(self, email):
        self.logger = logging.getLogger(__name__)
        super(Gravatar, self).__init__(email)

    def download_image(self, size=DEFAULT_IMAGE_SIZE, rating="g"):

        # Get the URL of the image
        image_url = super(Gravatar, self).get_image(size, "404", False, rating, True, True)

        try :
            # Download the image
            r = requests.get(image_url, stream=True)
            r.raise_for_status()

            # Decode and return the raw response
            r.raw.decode_content = True
            return r.raw

        # Catch any exception and don't return the raw response
        except requests.RequestException as err:
            logging.error(err)
            logging.debug(image_url)
            return False

    def chooseImage(self, images) :
        pass

