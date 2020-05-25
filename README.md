# Gravatar to Google Contacts
This is a Python package to copy Gravatar profile pictures to your Google Contacts.

## Description
When run as a script (by running `__main__.py`) the program will first ask a user to grant the Google Cloud Platform app access to their contacts in their Google Account. It will then download all of their contacts and remove those that don't have an email address and a name.

For each email address in each contact it will attempt to download the corresponding Gravatar photo. If a Gravatar photo is found for that contact then it will update the contact with that photo. If there are multiple possible Gravatar photos (due to a contact having multiple email addresses then a GUI will be presented to choose one. The user is notified which contacts have been updated, and those contacts have the custom `Gravatar Photo` field set to `"True"` (so that the program can safely update them in the future).

This program will not update contacts that already have a user-supplied photo that didn't previously come from Gravatar.

## Setup

### Dependencies
Note that the versions specified here are what I have been running it on, it may well work on older versions.
* Python>=3.7.4
* requests>=2.23.0
* google_api_python_client>=1.8.3
* google_auth_oauthlib>=0.4.1
* libgravatar>=0.2.3
* Pillow>=7.1.2
* protobuf>=3.12.1

### Creating a new Google Cloud Platform Project and enabling the People API 
You will need to create your own Google Cloud Platform Project, enable the People API, and create & download some OAuth 2.0 Client ID credentials as `credentials.json`. 

If you've not used Google Cloud Platform before then you can do all of this really easily by clicking on the large blue button labelled `Enable the People API` [here](https://developers.google.com/people/quickstart/python#step_1_turn_on_the). Choose to create a `Desktop app` and as per those instructions in resulting dialog click **DOWNLOAD CLIENT CONFIGURATION** and save the file `credentials.json` to your working directory.

Use of the Google People API is (at the time of writing) free.

Creating your own project helps to keep your contacts safe because you control the app that is asking to access them (and you can see my all of my source code here). You can revoke your app from accessing your contacts at [https://myaccount.google.com/permissions](https://myaccount.google.com/permissions). 


## Usage
`python gravatarcontacts` will run the program. Where necessary, the browser window and GUI will open automatically so this program should be run locally (and not over SSH for example).

## License
[GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/)


