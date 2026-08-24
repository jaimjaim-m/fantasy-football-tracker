from __future__ import annotations

import typer
from dotenv import set_key

from app.config import ROOT_DIR, get_settings
from app.espn.client import LeagueClient

app = typer.Typer(help="ff-league-hub commissioner tools")
cookies_app = typer.Typer(help="ESPN cookie helpers")
app.add_typer(cookies_app, name="cookies")


@cookies_app.command("validate")
def cookies_validate() -> None:
    """Check that SWID / espn_s2 still load the configured league."""
    get_settings.cache_clear()
    ok, message = LeagueClient().validate()
    typer.echo(message)
    raise typer.Exit(0 if ok else 1)


@cookies_app.command("extract")
def cookies_extract() -> None:
    """Open Chrome, let you log into ESPN, write SWID and ESPN_S2 into .env."""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
    except ImportError as exc:
        typer.echo(f"Install selenium extras first: {exc}")
        raise typer.Exit(1)

    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    try:
        driver.get("https://www.espn.com/fantasy/football/")
        typer.echo("Log into ESPN in the browser window, then return here and press Enter.")
        input()
        found: dict[str, str] = {}
        for cookie in driver.get_cookies() or []:
            name = cookie.get("name") or ""
            if name.lower() in {"swid", "espn_s2"}:
                found[name.lower()] = cookie.get("value") or ""
        if "swid" not in found or "espn_s2" not in found:
            typer.echo("Could not find both SWID and espn_s2. Stay on fantasy.espn.com after login and retry.")
            raise typer.Exit(1)
        env_path = ROOT_DIR / ".env"
        if not env_path.exists():
            env_path.write_text((ROOT_DIR / ".env.example").read_text())
        set_key(str(env_path), "SWID", found["swid"])
        set_key(str(env_path), "ESPN_S2", found["espn_s2"])
        get_settings.cache_clear()
        typer.echo(f"Wrote cookies to {env_path}. Re-deploy host secrets if this app is already in the cloud.")
        ok, message = LeagueClient().validate()
        typer.echo(message)
        raise typer.Exit(0 if ok else 1)
    finally:
        driver.quit()


if __name__ == "__main__":
    app()
