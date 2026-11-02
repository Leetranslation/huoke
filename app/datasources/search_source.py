"""搜索引擎数据源（桩）：后续接真实搜索 API / 海关数据。"""

from app.datasources.base import CompanyRaw, DataSource


class SearchDataSource(DataSource):
    """TODO(M3 之后)：接入搜索引擎/海关数据 API。当前为桩，返回空。"""

    def fetch(self) -> list[CompanyRaw]:
        return []
