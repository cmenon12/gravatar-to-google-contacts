"""
Script to update a user's Google contacts with Gravatar photos.

When run as a script (by running __main__.py) the program will first
ask a user to grant the Google Cloud Platform app access to their
contacts in their Google Account. It will then download all of their
contacts and remove those that don't have an email address and a name.

For each email address in each contact it will attempt to download the
corresponding Gravatar photo. If a Gravatar photo is found for that
contact then it will update the contact with that photo. If there are
multiple possible Gravatar photos (due to a contact having multiple
email addresses then a GUI will be presented to choose one. The user
is notified which contacts have been updated, and those contacts have
the custom Gravatar Photo field set to "True" (so that the program
can safely update them in the future).

This program will not update contacts that already have a user-supplied
photo that didn't previously come from Gravatar.
"""
import base64
import logging
import tkinter
from functools import partial
from io import BytesIO

from PIL import Image

from gravatarcontacts.google_contacts import Contact
from gravatarcontacts.gravatar import Gravatar, MAX_RATING

__author__ = "Christopher Menon"
__credits__ = "Christopher Menon"
__license__ = "gpl-3.0"

# Prepare the log
logging.basicConfig(filename="gravatarcontacts.log",
                    filemode="a",
                    format="%(asctime)s | %(levelname)s : %(message)s",
                    level=logging.DEBUG)


def main() -> None:
    """
    Updates a user's Google contacts with Gravatar photos.

    :return: None
    """

    # Connect to the service and fetch a list of the contacts
    service = Contact.authorize()
    contacts = Contact.list_contacts(service)

    # Get a Gravatar image for each email address in each contact
    # This will not save the image where it wasn't available
    for contact in contacts:
        if contact.has_user_photo is False or \
                contact.is_gravatar is True:
            for email in contact.emails:
                gravatar_image = Gravatar(email). \
                    download_image(MAX_RATING)
                if gravatar_image:
                    contact.gravatar_images.append(gravatar_image)

        # Remove duplicates from list of images
        contact.gravatar_images = list(dict.fromkeys(
            contact.gravatar_images))

        # Stop if there were no hits from Gravatar
        if len(contact.gravatar_images) == 0:
            logging.info("Contact has no Gravatars, "
                         "continuing with next contact.")
            continue

        # Choose one if there are too many
        if len(contact.gravatar_images) >= 2:
            logging.info("Contact has 2+ Gravatars, need to choose.")
            chosen_image = contact.gravatar_images[
                choose_image(contact.name, contact.gravatar_images)]
            contact.gravatar_images = [chosen_image]

        # Update the photo
        if contact.update_photo(service, contact.gravatar_images[0]) is True:
            print("Gravatar added for", contact.name)
        else:
            print("Gravatar could not be added for", contact.name)


def make_choice(root: tkinter.Tk, value: int):
    """
    Accepts the user's choice from the GUI and saves it as a global.
    :param root: the Tkinter GUI
    :param value: the chosen value
    :return: None
    """

    # Save the choice and close the window
    global answer
    answer = value
    root.destroy()
    logging.info("Answer chosen, Tkinter window destroyed.")
    logging.debug("User chose %d", value)


def choose_image(name: str, images: list) -> int:
    """
    Creates a GUI to choose a photo.

    This function creates a Tkinter GUI to prompt the user to choose a
    photo from the images list. If the user doesn't choose one and
    closes the window then the first is picked anyway (0 is returned).

    :param name: the contact name
    :param images: a list of the images as base64 strings
    :return: the index of the chosen image
    """

    # Using a default value of 0 in case they just close it
    global answer
    answer = 0

    # Set up GUI
    root = tkinter.Tk()
    tkinter.Label(root, text="Choose a Gravatar profile picture for " +
                             name).grid(row=0, column=0,
                                        columnspan=len(images))

    # Prepare for loop
    counter = 0
    buttons = []

    for image in images:

        # Resize the image to 200x200
        buffered = BytesIO()
        Image.open(BytesIO(base64.b64decode(image))).\
            resize((200, 200)).save(buffered, format="PNG")
        image_gui_str = base64.b64encode(buffered.getvalue())
        image_gui_obj = tkinter.PhotoImage(data=image_gui_str)

        # Create a button with the image
        buttons.append(tkinter.Button(root, image=image_gui_obj,
                                      command=partial(make_choice,
                                                      root, counter)))
        buttons[counter].photo = image_gui_obj
        buttons[counter].grid(row=2, column=counter)
        logging.info("Button created for image %d", counter)
        counter += 1

    # Display the GUI and get an answer
    # We delete the global to stay safe
    print("Please choose a profile picture for " + name +
          " in the GUI window.")
    logging.info("Creating GUI.")
    root.mainloop()
    value = answer
    del answer

    assert 0 <= value < len(images)

    return value


if __name__ == "__main__":
    logging.info("Running gravatarcontacts.__main__.main()")
    main()
