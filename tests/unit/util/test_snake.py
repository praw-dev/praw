from praw.util import camel_to_snake, snake_case_keys

from .. import UnitTest


class TestSnake(UnitTest):
    def test_camel_to_snake(self):
        test_strings = (
            ("camelCase", "camel_case"),
            ("PascalCase", "pascal_case"),
            ("camelCasePlace", "camel_case_place"),
            ("Pascal8Camel8Snake", "pascal8_camel8_snake"),
            ("HTTPResponseCode", "http_response_code"),
            ("ResponseHTTP", "response_http"),
            ("ResponseHTTP200", "response_http200"),
            ("getHTTPResponseCode", "get_http_response_code"),
            ("get200HTTPResponseCode", "get200_http_response_code"),
            ("getHTTP200ResponseCode", "get_http200_response_code"),
            ("12PolarBears", "12_polar_bears"),
            ("11buzzingBees", "11buzzing_bees"),
            ("TacocaT", "tacoca_t"),
            ("fooBARbaz", "foo_ba_rbaz"),
            ("foo_BAR_baz", "foo_bar_baz"),
            ("Base_BASE", "base_base"),
            ("Case_Case", "case_case"),
            ("FACE_Face", "face_face"),
        )
        for camel, snake in test_strings:
            assert camel_to_snake(camel) == snake

    def test_camel_to_snake_dict(self):
        test_strings = {
            "camelCase": "camel_case",
            "PascalCase": "pascal_case",
            "camelCasePlace": "camel_case_place",
            "Pascal8Camel8Snake": "pascal8_camel8_snake",
            "HTTPResponseCode": "http_response_code",
            "ResponseHTTP": "response_http",
            "ResponseHTTP200": "response_http200",
            "getHTTPResponseCode": "get_http_response_code",
            "get200HTTPResponseCode": "get200_http_response_code",
            "getHTTP200ResponseCode": "get_http200_response_code",
            "12PolarBears": "12_polar_bears",
            "11buzzingBees": "11buzzing_bees",
            "TacocaT": "tacoca_t",
            "fooBARbaz": "foo_ba_rbaz",
            "foo_BAR_baz": "foo_bar_baz",
            "Base_BASE": "base_base",
            "Case_Case": "case_case",
            "FACE_Face": "face_face",
        }
        new_test = snake_case_keys(test_strings)
        for key, item in new_test.items():
            assert key == item
