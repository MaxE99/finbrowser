from __future__ import absolute_import, unicode_literals
from datetime import timedelta
from base64 import b64encode
from typing import Any, Dict

import requests

from django.utils import timezone


class SpotifyAPI(object):
    """
    A client to interact with the Spotify API for accessing podcast episodes
    and podcaster information.
    """

    access_token = None
    access_token_expires = timezone.now()
    access_token_did_expire = True
    client_id = None
    client_secret = None
    token_url = "https://accounts.spotify.com/api/token"

    def __init__(
        self, client_id: str, client_secret: str, *args: Any, **kwargs: Any
    ) -> None:
        """
        Initializes the SpotifyAPI client.

        Args:
            client_id (str): The Spotify client ID.
            client_secret (str): The Spotify client secret.
        """
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret

    def get_client_credentials(self) -> str:
        """
        Encodes the client ID and client secret for authorization.

        Raises:
            Exception: If client_id or client_secret is not set.

        Returns:
            str: The base64 encoded client credentials.
        """
        if self.client_id is None or self.client_secret is None:
            raise Exception("You must set client_id and client_secret")
        client_creds = f"{self.client_id}:{self.client_secret}"
        return b64encode(client_creds.encode()).decode()

    def get_token_headers(self) -> Dict[str, str]:
        """
        Constructs the headers for the token request.

        Returns:
            dict: A dictionary containing the authorization header.
        """
        client_creds_b64 = self.get_client_credentials()
        return {"Authorization": f"Basic {client_creds_b64}"}

    def get_token_data(self) -> Dict[str, str]:
        """
        Prepares the data for the token request.

        Returns:
            dict: A dictionary containing the grant type.
        """
        return {"grant_type": "client_credentials"}

    def perform_auth(self) -> bool:
        """
        Requests an access token from the Spotify API.

        Raises:
            Exception: If the authentication request fails.

        Returns:
            bool: True if authentication is successful.
        """
        request = requests.post(
            self.token_url,
            data=self.get_token_data(),
            headers=self.get_token_headers(),
            timeout=10,
        )
        if request.status_code not in range(200, 299):
            raise Exception("Could not authenticate client.")

        data = request.json()
        expires_in = data["expires_in"]
        self.access_token = data["access_token"]
        self.access_token_expires = timezone.now() + timedelta(seconds=expires_in)
        self.access_token_did_expire = self.access_token_expires < timezone.now()
        return True

    def get_access_token(self) -> str:
        """
        Retrieves a valid access token, refreshing it if necessary.

        Returns:
            str: A valid access token for API requests.
        """
        if self.access_token is None or self.access_token_expires < timezone.now():
            self.perform_auth()
        return self.access_token

    def get_episodes(self, id: str) -> Dict[str, Any]:
        """
        Fetches the episodes of a given podcast show by its ID.

        Args:
            id (str): The Spotify ID of the podcast show.

        Returns:
            dict: A dictionary containing the episodes data or an empty dictionary on error.
        """
        access_token = self.get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        lookup_url = f"https://api.spotify.com/v1/shows/{id}/episodes?market=US"
        request = requests.get(lookup_url, headers=headers, timeout=10)

        if request.status_code not in range(200, 299):
            return {}
        return request.json()

    def get_podcaster(self, id: str) -> Dict[str, Any]:
        """
        Fetches podcaster information by the show ID.

        Args:
            id (str): The Spotify ID of the podcast show.

        Returns:
            dict: A dictionary containing the podcaster data or an empty dictionary on error.
        """
        access_token = self.get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        lookup_url = f"https://api.spotify.com/v1/shows/{id}?market=US"
        request = requests.get(lookup_url, headers=headers, timeout=10)

        if request.status_code not in range(200, 299):
            return {}
        return request.json()
