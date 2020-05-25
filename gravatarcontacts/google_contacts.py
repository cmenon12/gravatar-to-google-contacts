"""
Facilitates access to Google Contacts using the People API

This module connects to the People API, allowing you to download a list
of contacts for the purpose of updating their photos. Each downloaded
contact is instantiated as a Contact, and can then have its photo
updated.
"""

import logging
import os
import pickle

import googleapiclient
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

__author__ = "Christopher Menon"
__credits__ = ["Christopher Menon",
               "https://developers.google.com/people/quickstart/python"]
__license__ = "gpl-3.0"

# This variable specifies the name of a file that contains the
# OAuth 2.0 information for this application, including its client_id
# and client_secret.
CLIENT_SECRETS_FILE = "credentials.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL
# connection.
SCOPES = ["https://www.googleapis.com/auth/contacts"]
API_SERVICE_NAME = "contacts"
API_VERSION = "v1"

# This file stores the user's access and refresh tokens and is created
# automatically when the authorization flow completes for the first
# time. This specifies where the file is stored
TOKEN_PICKLE_FILE = "token.pickle"


class Contact:
    """
    Facilitates interaction with the Google People API.
    
    Portions of this class are modifications based on work created
    and shared by Google and used according to terms described in the
    Apache 2.0 License Attribution License.
    """

    def __init__(self, res_name: str, name: str, emails: list,
                 has_user_photo: bool, is_gravatar: bool, etag: str):
        self.res_name = res_name
        self.name = name
        self.emails = emails
        self.has_user_photo = has_user_photo
        self.is_gravatar = is_gravatar
        self.gravatar_images = []
        self.etag = etag

    @staticmethod
    def authorize() -> googleapiclient.discovery.Resource:
        """
        Connects to and authenticates the People API, returning the service.

        This function first checks for valid credentials, if none exist (or
        if they are invalid) then a browser window is opened to ask the user
        to authenticate using a Google Account. Because this app uses
        sensitive scopes, user's are warned before authenticating unless
        the Google Cloud Platform app has been approved by Google.

        :return: the People API service (a Resource)
        """

        credentials = None

        # Attempt to access pre-existing credentials
        if os.path.exists(TOKEN_PICKLE_FILE):
            with open(TOKEN_PICKLE_FILE, 'rb') as token:
                credentials = pickle.load(token)

        # If there are no (valid) credentials available let the user log in.
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CLIENT_SECRETS_FILE, SCOPES)
                credentials = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open(TOKEN_PICKLE_FILE, "wb") as token:
                pickle.dump(credentials, token)

        # Create and return the authenticated service
        service = build('people', 'v1', credentials=credentials)
        logging.info("People API service created.")
        return service

    @staticmethod
    def list_contacts(service: googleapiclient.discovery.Resource) -> list:
        """
        Fetches the user's contacts as a list.

        This will fetch the user's contacts that have a name and an email
        address. It will return them as a list of Contact objects.

        :param service: the People API service (a Resource)
        :return: a list of Contact objects
        """

        # Fetch the user's contacts (up to 2000)
        results = service.people().connections().list(
            resourceName='people/me',
            pageSize=2000,
            personFields='names,emailAddresses,photos,UserDefined').execute()
        connections = results.get('connections', [])
        logging.info("Contacts retrieved.")
        contacts = []

        for contact in connections:

            # Get the contact resource name
            res_name = contact["resourceName"]
            etag = contact["etag"]

            # Get the name and email address
            # If both aren't there then skip the contact
            emails = []
            if "names" in contact and "emailAddresses" in contact:
                name = contact["names"][0]["displayName"]
                for email in contact["emailAddresses"]:
                    emails.append(email["value"])
            else:
                logging.info("Contact skipped.")
                continue

            # Determine if the contact already has a user-supplied photo
            # This will stay false there's a photo from their Google profile
            # photo["default"] is only present if it's true,
            # so if it's not there then this is not the default
            has_user_photo = False
            if "photos" in contact:
                for photo in contact["photos"]:
                    if photo["metadata"]["source"]["type"] == "CONTACT" and \
                            "default" not in photo:
                        has_user_photo = True

            # Determine if that photo was already supplied from Gravatar
            # This will stay false if has_user_photo is false
            is_gravatar = False
            if "userDefined" in contact:
                for custom in contact["userDefined"]:
                    if custom["key"] == "Gravatar Photo" and \
                            custom["value"] == "True":
                        is_gravatar = True

            # Save this contact's details
            contacts.append(Contact(res_name, name, emails,
                                    has_user_photo, is_gravatar, etag))
            logging.info("New contact saved")
            logging.debug("New contact called %s with res name %s",
                          name, res_name)

        return contacts

    def update_photo(self, service: googleapiclient.discovery.Resource,
                     new_photo: str) -> bool:
        """
        Updates the photo of the contact with the Gravatar photo.

        This method updates the photo of the contact with the supplied
        photo, and records that the photo came from Gravatar (by setting
        the custom Gravatar Photo field set to True.

        :param service: the People API service (a Resource)
        :param new_photo: the new photo as a base-64 encoded string
        :return: True on success, False on failure
        """

        logging.debug("Updating photo for %s with res name %s",
                      self.name, self.res_name)

        try:

            # Save to the contact that the photo is from Gravatar
            service.people().updateContact(
                resourceName=self.res_name,
                updatePersonFields="userDefined",
                body={"etag": self.etag,
                      "userDefined": [{"key": "Gravatar Photo",
                                       "value": "True"}]}).execute()
            logging.info("Contact updated with custom field Gravatar=True.")

            # Update the photo
            service.people().updateContactPhoto(
                resourceName=self.res_name,
                body={"photoBytes": new_photo}).execute()
            logging.info("Contact photo updated.")

            return True

        except Exception as err:
            print(err)
            return False
