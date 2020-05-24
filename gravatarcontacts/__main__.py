from gravatar import Gravatar
import google_contacts
import tkinter
from PIL import Image
from io import BytesIO
import base64
from functools import partial

def main():
    # Connect to the service and fetch a list of the contacts
    service = google_contacts.authorize()
    contacts = google_contacts.list_contacts(service)

    # Get a Gravatar image for each email address in each contact
    # This will not save the image where it wasn't available
    for contact in contacts:
        if contact.has_user_photo is False or contact.is_gravatar is True:
            for email in contact.emails:
                gravatar_image = Gravatar(email).download_image()
                if gravatar_image:
                    contact.gravatar_images.append(gravatar_image)

        # Remove duplicates from list of images
        contact.gravatar_images = list(dict.fromkeys(contact.gravatar_images))

        # Stop if there were no hits from Gravatar
        if len(contact.gravatar_images) == 0:
            continue

        # Choose one if there are too many
        elif len(contact.gravatar_images) >= 2:
            chosen_image = contact.gravatar_images[choose_image(contact.name,
                                                                contact.gravatar_images)]
            contact.gravatar_images = [chosen_image]

        # Update the photo
        contact.update_photo(service, contact.gravatar_images[0])

        print("Gravatar added for", contact.name)

def make_choice(root, value):

    # Save the choice and close the window
    global answer
    answer = value
    root.destroy()

def choose_image(name, images):

    # Using a default value of 0 in case they just close it
    global answer
    answer = 0

    # Set up GUI
    root = tkinter.Tk()
    tkinter.Label(root, text="Choose a Gravatar photo for " + name).grid(row=0, column=0, columnspan=len(images))

    # Prepare for loop
    counter = 0
    buttons = []

    for image in images:

        # Resize the image to 200x200
        buffered = BytesIO()
        Image.open(BytesIO(base64.b64decode(image))).resize((200, 200)).save(buffered, format="PNG")  # use JPEG
        image_gui_str = base64.b64encode(buffered.getvalue())
        image_gui_obj = tkinter.PhotoImage(data=image_gui_str)

        # Create a button with the image
        buttons.append(tkinter.Button(root, image=image_gui_obj, command=partial(make_choice, root, counter)))
        buttons[counter].photo = image_gui_obj
        buttons[counter].grid(row=2, column=counter)
        counter += 1

    # Display the GUI and get an answer
    # We delete the global to stay safe
    root.mainloop()
    value = answer
    del answer
    return value


if __name__ == "__main__":
    main()

