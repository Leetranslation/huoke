"""线索过滤与邮箱分级规则（纯函数，不联网）。"""

from app.api.routes.campaigns import _looks_like_article, _rank_emails


class TestArticleFilter:
    """判断一个标题是不是「公司名」，而不是文章/机构/栏目页。"""

    def test_news_headline_rejected(self):
        assert _looks_like_article(
            "Governor Meyer Announces $380M Advanced Manufacturing Project"
        )

    def test_long_title_rejected(self):
        assert _looks_like_article("A" * 61)

    def test_howto_article_rejected(self):
        assert _looks_like_article("How to choose a hydraulic supplier")

    def test_top_list_rejected(self):
        assert _looks_like_article("Top 10 hydraulic manufacturers in Germany")

    def test_institution_rejected(self):
        assert _looks_like_article("University of Dayton Research Institute")
        assert _looks_like_article("412TH TEST WING TEST CAPABILITIES")

    def test_real_company_kept(self):
        assert not _looks_like_article("Hans Hydraulik GmbH")
        assert not _looks_like_article("Maxpro Technologies")
        assert not _looks_like_article("EnBW AG")

    def test_empty_safe(self):
        assert not _looks_like_article("")


class TestEmailRanking:
    """邮箱分级：剔除 HR/系统/学校，采购类优先。"""

    def test_useless_emails_removed(self):
        out = _rank_emails(
            [
                "hr@genlp.com",
                "notify@dayforce.com",
                "noreply@acme.com",
                "privacy@acme.com",
                "m@udayton.edu",
                "s@udayton.edu",
            ]
        )
        assert out == []

    def test_edu_gov_removed(self):
        assert _rank_emails(["someone@mit.edu", "info@agency.gov"]) == []

    def test_purchasing_first(self):
        out = _rank_emails(
            [
                "john.doe@acme.com",
                "purchasing@acme.com",
                "sales@acme.com",
            ]
        )
        assert out[0] == "purchasing@acme.com"
        assert len(out) == 3

    def test_personal_email_kept(self):
        out = _rank_emails(["john.doe@acme.com"])
        assert out == ["john.doe@acme.com"]

    def test_preserves_input_order_within_same_rank(self):
        out = _rank_emails(["b@x.com", "a@x.com"])
        assert out == ["b@x.com", "a@x.com"]
