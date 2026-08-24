from __future__ import annotations

from espn_api.football import League
from espn_api.requests.espn_requests import ESPNAccessDenied, ESPNInvalidLeague

from app.config import Settings, get_settings
from app.espn.cache import TTLCache


class ESPNAccessError(Exception):
    """Cookies missing, expired, or league inaccessible."""


def owner_name(team) -> str | None:
    owners = getattr(team, "owners", None) or []
    if not owners:
        return None
    owner = owners[0]
    if isinstance(owner, dict):
        display = owner.get("displayName")
        if display:
            return display
        first = owner.get("firstName") or ""
        last = owner.get("lastName") or ""
        name = f"{first} {last}".strip()
        return name or None
    return str(owner)


class LeagueClient:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._cache: TTLCache[League] = TTLCache(self.settings.cache_ttl_seconds)

    def get_league(self, year: int | None = None) -> League:
        season = year or self.settings.year
        key = f"league:{self.settings.league_id}:{season}"
        cached = self._cache.get(key)
        if cached is not None:
            return cached
        league = self._fetch(season)
        return self._cache.set(key, league)

    def _fetch(self, year: int) -> League:
        try:
            return League(
                league_id=self.settings.league_id,
                year=year,
                espn_s2=self.settings.espn_s2,
                swid=self.settings.swid,
            )
        except ESPNAccessDenied as exc:
            raise ESPNAccessError(
                "ESPN denied access. SWID/espn_s2 cookies are missing, invalid, or expired."
            ) from exc
        except ESPNInvalidLeague as exc:
            raise ESPNAccessError(f"League {self.settings.league_id} was not found for {year}.") from exc
        except Exception as exc:
            message = str(exc).lower()
            if any(token in message for token in ("unauthorized", "401", "403", "forbidden", "cookie")):
                raise ESPNAccessError("ESPN cookies appear invalid or expired.") from exc
            raise

    def validate(self) -> tuple[bool, str]:
        try:
            league = self.get_league()
            name = league.settings.name
            return True, f"Connected to {name} ({league.year})"
        except ESPNAccessError as exc:
            return False, str(exc)
        except Exception as exc:
            return False, f"Could not reach ESPN: {exc}"


def validate_cookies(settings: Settings | None = None) -> tuple[bool, str]:
    return LeagueClient(settings).validate()
