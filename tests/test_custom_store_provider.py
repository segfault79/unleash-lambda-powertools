import unittest
from typing import Any
from unittest import mock

from aws_lambda_powertools.utilities.feature_flags import FeatureFlags
from custom_store_provider import unleash_store_provider

unleash_api_base_url = 'https://eu.app.unleash-hosted.com/demo/api'
unleash_api_token = 'justtesting'
unleash_project_id = 'demo-app'


def mocked_requests_get(*args, **kwargs):
    """
    This method will be used by the mock to replace requests.get().
    """

    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == 'https://eu.app.unleash-hosted.com/demo/api/client/features':
        return MockResponse({
            "features": [
                {
                    "name": "ten_percent_off_campaign",
                    "enabled": True,
                    "project": "demo-app"
                },
                {
                    "name": "free_shipping_campaign",
                    "enabled": False,
                    "project": "demo-app"
                }
            ]
        }, 200)

    return MockResponse(None, 404)


class MyGreatClassTestCase(unittest.TestCase):

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_fetch(self, mock_get):
        # test
        unleash_config_store = unleash_store_provider.UnleashStoreProvider(unleash_api_base_url, unleash_api_token, unleash_project_id)
        feature_flags = FeatureFlags(store=unleash_config_store)

        # verify
        apply_discount: Any = feature_flags.evaluate(name="ten_percent_off_campaign", default=False)
        assert apply_discount == True

        apply_discount: Any = feature_flags.evaluate(name="free_shipping_campaign", default=False)
        assert apply_discount == False


if __name__ == '__main__':
    unittest.main()
