import os
from typing import Any, Dict

import requests
from aws_lambda_powertools import Logger

from aws_lambda_powertools.utilities.feature_flags.base import StoreProvider
from aws_lambda_powertools.utilities.feature_flags.exceptions import ConfigurationStoreError
from botocore.exceptions import ClientError

unlesh_api_timeout = os.getenv("UNLEASH_API_TIMEOUT", 5)

logger = Logger()


class UnleashStoreProvider(StoreProvider):
    features = None

    def __init__(self, unleash_api_base_url: str, unleash_api_token: str, unleash_project: str):
        super().__init__()

        self.unleash_api_base_url = unleash_api_base_url
        self.unleash_api_token = unleash_api_token
        self.unleash_project = unleash_project

    def _get_features_from_unleash(self) -> Dict[str, Any]:
        if self.features is not None:
            logger.debug("Cache hit: reusing features from local cache.")
            return self.features

        logger.debug("Cache miss: fetching features from Unleash API.")

        try:
            response = requests.get(
                f"{self.unleash_api_base_url}/client/features",
                timeout=unlesh_api_timeout,
                headers={
                    "Accept": "application/json",
                    "Authorization": f"{self.unleash_api_token}",
                    "UNLEASH-APPNAME": f"{self.unleash_project}"
                }
            )

            if response.status_code != 200:
                raise ConfigurationStoreError(f"Unable to get features from Unleash API: {response.status_code}")

            self.features = {}
            for f in response.json()['features']:
                self.features[f['name']] = {
                    "default": f['enabled']
                }

            logger.debug("Successfully retrieved features from Unleash API.")
            return self.features
        except ClientError as exc:
            raise ConfigurationStoreError("Unable to get features from Unleash API.") from exc

    def get_configuration(self) -> Dict[str, Any]:
        """
        Get_raw_configuration() – get the raw configuration from the store provider and return the parsed JSON dictionary.
        :return:
        """
        return self._get_features_from_unleash()

    @property
    def get_raw_configuration(self) -> Dict[str, Any]:
        """
        Get the configuration from the store provider, parsing it as a JSON dictionary. If an envelope is set, extract the envelope data.
        :return:
        """
        return self._get_features_from_unleash()
