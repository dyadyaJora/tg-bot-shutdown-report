import re

import yaml


def trim_report(report_text, n, m):
    trimmed_str = report_text[n:len(report_text)-m]
    return trimmed_str


def parse_yaml_data_from_report_message(input_string):
    match = re.search(r'.*====(?P<data>.*?)====.*', input_string, re.DOTALL)

    if match:
        yaml_data = match.group('data')

        try:
            parsed_data = yaml.safe_load(yaml_data)
            return parsed_data
        except yaml.YAMLError as e:
            print("Ошибка парсинга YAML:", e)
            return None
    else:
        print("Текст не найден по заданному паттерну")
        return None
