"""CSV 数据源：从 CSV 文件导入公司线索。"""

import csv
from pathlib import Path

from app.datasources.base import CompanyRaw, DataSource


class CsvDataSource(DataSource):
    """读取 CSV（列：name, website, country, industry）。"""

    def __init__(self, path: str | Path):
        self._path = Path(path)

    def fetch(self) -> list[CompanyRaw]:
        companies: list[CompanyRaw] = []
        with self._path.open(encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                companies.append(
                    CompanyRaw(
                        name=(row.get("name") or "").strip(),
                        website=(row.get("website") or "").strip(),
                        country=(row.get("country") or "").strip(),
                        industry=(row.get("industry") or "").strip(),
                        source="csv",
                    )
                )
        return companies
