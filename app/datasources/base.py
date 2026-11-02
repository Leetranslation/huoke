"""数据源抽象接口：可插拔的线索来源。"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class CompanyRaw:
    """数据源产出的原始公司线索（尚未入库）。"""

    name: str
    website: str = ""
    country: str = ""
    industry: str = ""
    description: str = ""
    source: str = ""


class DataSource(ABC):
    """线索数据源接口。新增数据源只需实现 fetch，不改业务代码。"""

    @abstractmethod
    def fetch(self) -> list[CompanyRaw]:
        """拉取一批公司线索。"""
        raise NotImplementedError
