# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "credentials.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ["https://www.googleapis.com/auth/contacts"]
API_SERVICE_NAME = "contacts"
API_VERSION = "v1"

# One of g, pg, r, or x
MAX_RATING = "g"

# This specifies where the token.pickle is stored
TOKEN_PICKLE_FILE = "token.pickle"