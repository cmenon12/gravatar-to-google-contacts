import logging

DEFAULT_IMAGE_SIZE = 400

# Prepare the log
logging.basicConfig(filename="gravatar_to_contacts.log",
                    filemode="a",
                    format="%(asctime)s | %(levelname)s : %(message)s",
                    level=logging.DEBUG)