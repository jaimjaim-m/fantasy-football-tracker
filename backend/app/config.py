from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(str(ROOT_DIR / ".env"), ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # When true, all APIs use a built-in sample league (no ESPN cookies needed).
    demo_mode: bool = False
    league_id: int = 0
    year: int = 2025
    swid: str = ""
    espn_s2: str = ""
    hub_password: str = ""
    cache_ttl_seconds: int = 180
    history_start_year: int = 2016
    playoff_teams: int = 6
    h2h_win_points: int = 2
    top_n_bonus: int = 6
    top_n_points: int = 1
    static_dir: Optional[Path] = None

    @property
    def resolved_static_dir(self) -> Path:
        if self.static_dir is not None:
            return Path(self.static_dir)
        env_static = Path("/app/static")
        if env_static.is_dir():
            return env_static
        return ROOT_DIR / "frontend" / "dist"


@lru_cache
def get_settings() -> Settings:
    return Settings()
