# unleash-lambda-powertools

Demonstrates a very simple integration of the [Unlesh Feature Management](https://www.getunleash.io/) API with AWS
Lambda and [Powertools for AWS Lambda](https://docs.powertools.aws.dev/lambda/python/latest/utilities/feature_flags/).

## Tests

```
pip install -r requirements.txt
pip install -r requirements_test.txt

python -m pytest -vvv tests/
```

## How to use

```python
import os
from typing import Any

from aws_lambda_powertools.utilities.feature_flags import FeatureFlags
from aws_lambda_powertools.utilities.typing import LambdaContext
from custom_store_provider.unleash_store_provider import UnleashStoreProvider

unleash_api_base_url = os.getenv('UNLEASH_API_BASE_URL')
unleash_api_token = os.getenv('UNLEASH_API_TOKEN')
unleash_project_id = os.getenv('UNLEASH_PROJECT_ID')

unleash_config_store = UnleashStoreProvider(unleash_api_base_url, unleash_api_token, unleash_project_id)
feature_flags = FeatureFlags(store=unleash_config_store)


def lambda_handler(event: dict, context: LambdaContext):
    price: Any = event.get("price")

    apply_discount: Any = feature_flags.evaluate(name="ten_percent_off_campaign", default=False)
    if apply_discount:
        price = price * 0.9

    return {"price": price}
```