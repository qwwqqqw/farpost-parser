from typing import Dict

def normalize_params(params: list) -> Dict[str, str]:

    result = {}

    for param in params:

        if not isinstance(param, dict):

            continue

        param_type = param.get('type')

        value = param.get('value')

        if param_type and value:

            if isinstance(value, list):

                result[param_type] = ','.join(str(v) for v in value)

            else:

                result[param_type] = str(value)

    return result

def build_api_params(search_core: dict) -> dict:

    params = {}

    base_keys = [

        'categoryId',

        'locationId',

        'verticalCategoryId',

        'rootCategoryId',

        'localPriority',

        'geoCoords',

    ]

    for key in base_keys:

        value = search_core.get(key)

        if value not in (None, [], ''):

            params[key] = str(value)

    if search_core.get('priceMax'):

        params['pmax'] = search_core['priceMax']

    if search_core.get('priceMin'):

        params['pmin'] = search_core['priceMin']

    if search_core.get('owner'):

        params['user'] = search_core['owner']

    if search_core.get('withDeliveryOnly'):

        params['cd'] = 1

    if search_core.get('searchRadius'):

        params['radius'] = search_core['searchRadius']

    if search_core.get('params'):

        params.update(normalize_params(search_core['params']))

    return params
