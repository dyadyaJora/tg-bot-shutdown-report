import json
import re
from datetime import datetime

import yaml


class Report:
    def __init__(self, provider_value, region_value, url, comment_value, status='',
                 time=datetime.utcnow().isoformat() + "Z", is_vpn_used=None, vpn_provider=None, vpn_protocol=None,
                 services=None):
        self.provider_value = provider_value
        self.region_value = region_value
        self.url = url
        self.comment_value = comment_value
        self.status = status
        self.time = time
        self.is_vpn_used = is_vpn_used
        self.vpn_provider = vpn_provider
        self.vpn_protocol = vpn_protocol
        self.services = services

    @staticmethod
    def convert_keys_to_snake_case(data):
        snake_case_data = {}
        for key, value in data.items():
            snake_case_key = re.sub(r'(?<!^)(?=[A-Z])', '_', key).lower()
            snake_case_data[snake_case_key] = value
        return snake_case_data

    @staticmethod
    def from_camel_case_yaml(yaml_data):
        parsed_data = yaml.safe_load(yaml_data)
        snake_case_data = Report.convert_keys_to_snake_case(parsed_data)
        return Report(**snake_case_data)

    @staticmethod
    def from_yaml(yaml_data):
        parsed_data = yaml.safe_load(yaml_data)
        return Report(**parsed_data)

    @staticmethod
    def from_json(json_data):
        parsed_data = json.loads(json_data)
        snake_case_data = Report.convert_keys_to_snake_case(parsed_data)
        return Report(**snake_case_data)
