"""LLM 返回值的解析与域名推断（纯逻辑，不调 LLM）。"""

from app.agent.entity_extractor import EntityExtractor
from app.datasources.tavily_source import _name_from_url, _pick_name


class TestEntityJsonParse:
    def test_plain_json(self):
        data = EntityExtractor._parse('{"companies": [{"idx": 0, "name": "EnBW AG"}]}')
        assert data["companies"][0]["name"] == "EnBW AG"

    def test_fenced_json(self):
        raw = '```json\n{"companies": [{"idx": 1, "name": "Siemens"}]}\n```'
        assert EntityExtractor._parse(raw)["companies"][0]["name"] == "Siemens"

    def test_json_with_surrounding_text(self):
        raw = '好的，结果如下：\n{"companies": [{"idx": 2, "name": "Plug Power"}]}\n以上。'
        assert EntityExtractor._parse(raw)["companies"][0]["name"] == "Plug Power"

    def test_invalid_returns_empty(self):
        assert EntityExtractor._parse("完全不是 JSON") == {}

    def test_empty_safe(self):
        assert EntityExtractor._parse("") == {}


class TestNameFromUrl:
    def test_simple_domain(self):
        assert _name_from_url("https://www.enbw.com/company/topics/hydrogen") == "Enbw"

    def test_two_part_tld(self):
        assert _name_from_url("https://www.hydro-funk.co.uk/about") == "Hydro Funk"

    def test_subdomain(self):
        assert _name_from_url("https://shop.acme-hydraulics.com/x") == "Acme Hydraulics"

    def test_no_protocol(self):
        assert _name_from_url("enbw.com") == "Enbw"

    def test_invalid(self):
        assert _name_from_url("") == ""


class TestPickName:
    def test_uses_clean_title(self):
        assert _pick_name("EnBW AG", "https://enbw.com") == "EnBW AG"

    def test_strips_suffix(self):
        assert _pick_name("Hydrogen | Company | EnBW", "https://enbw.com") == "Hydrogen"

    def test_falls_back_to_domain_for_page_title(self):
        # "Station Map" 是栏目页，应该回退到域名
        assert _pick_name("Station Map", "https://www.schaeffler.com/x") == "Schaeffler"

    def test_page_noise_companies(self):
        assert _pick_name("Oil and Gas Companies", "https://www.oge.net/x") == "Oge"

    def test_long_title_falls_back(self):
        long_title = "Governor Meyer Announces $380M Advanced Manufacturing Project"
        assert _pick_name(long_title, "https://www.lhyfe.com/press") == "Lhyfe"
