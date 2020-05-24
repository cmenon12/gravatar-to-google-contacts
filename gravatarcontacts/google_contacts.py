from dotenv import load_dotenv
from pathlib import Path
import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

env_path = Path(os.getcwd()).parent.absolute() / ".env"
load_dotenv(dotenv_path=env_path)
API_KEY = os.getenv("GOOGLE_CLOUD_API_KEY_FOR_PEOPLE_API")

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "credentials.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ["https://www.googleapis.com/auth/contacts"]
API_SERVICE_NAME = 'contacts'
API_VERSION = 'v1'


def authorize():
    """Shows basic usage of the People API.
    Prints the name of the first 10 connections.
    """
    credentials = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            credentials = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)

    service = build('people', 'v1', credentials=credentials)

    return service


def list_contacts(service):
    # Fetch the user's contacts (names and emails)
    # This can fetch up to 2000
    results = service.people().connections().list(
        resourceName='people/me',
        pageSize=2000,
        personFields='names,emailAddresses,photos,UserDefined').execute()
    connections = results.get('connections', [])
    contacts = []

    for contact in connections:

        # Get the contact resource name
        contact_res_name = contact["resourceName"]
        etag = contact["etag"]

        # Get the name
        # If there's no name then skip the contact
        if "names" in contact:
            name = contact["names"][0]["displayName"]
        else:
            continue

        # Get the email
        # If there's no email then skip the contact
        emails = []
        if "emailAddresses" in contact:
            for email in contact["emailAddresses"]:
                emails.append(email["value"])
        else:
            continue

        # Determine if the contact already has a user-supplied photo
        # This will stay false if it has a photo from their Google profile
        # photo["default"] is only present if it's true, so if it's not there then this is not the default
        has_user_photo = False
        if "photos" in contact:
            for photo in contact["photos"]:
                if photo["metadata"]["source"]["type"] == "CONTACT" and "default" not in photo:
                    has_user_photo = True

        # Determine if that photo was already supplied from Gravatar
        # This will stay false if has_user_photo is false
        is_gravatar = False
        if "userDefined" in contact:
            for custom in contact["userDefined"]:
                if custom["key"] == "Gravatar Photo" and custom["value"] == "True":
                    is_gravatar = True

        # Save this contact's details
        contacts.append(Contact(contact_res_name, name, emails, has_user_photo, is_gravatar, etag))

    return contacts


class Contact:

    def __init__(self, res_name, name, emails, has_user_photo, is_gravatar, etag):
        self.res_name = res_name
        self.name = name
        self.emails = emails
        self.has_user_photo = has_user_photo
        self.is_gravatar = is_gravatar
        self.gravatar_images = []
        self.etag = etag

    def update_photo(self, service, new_photo):

        try:

            # Save to the contact that the photo is from Gravatar
            service.people().updateContact(
                resourceName=self.res_name,
                updatePersonFields="userDefined",
                body={"etag": self.etag,
                      "userDefined": [{"key": "Gravatar Photo", "value": "True"}]}).execute()

            # Update the photo
            service.people().updateContactPhoto(
                resourceName=self.res_name,
                body={"photoBytes": new_photo}).execute()

            return True
        except Exception as e:
            print(e)
            return False