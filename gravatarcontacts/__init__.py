import logging

# Prepare the log
logging.basicConfig(filename="gravatarcontacts.log",
                    filemode="a",
                    format="%(asctime)s | %(levelname)s : %(message)s",
                    level=logging.DEBUG)
