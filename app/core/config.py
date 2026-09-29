from pathlib import Path
from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Customer Search API"
    app_version: str = "1.0.0"
    base_dir: Path = Path(__file__).resolve().parent.parent.parent
    data_dir: Path = base_dir / "data"
    customers_file_path: Path = data_dir / "customers.json"


settings = Settings()
