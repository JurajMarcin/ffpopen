from configparser import ConfigParser
from dataclasses import dataclass
from os import environ
from pathlib import Path
from re import search
from subprocess import run
from sys import argv
from tkinter import Button, Tk
from tomllib import loads as toml_loads
from typing import Any


PROFILES_PATH = (
    (
        Path(environ["FFPOPEN_PROFILES"])
        if "FFPOPEN_PROFILES" in environ
        else (
            Path(environ["XDG_CONFIG_HOME"], "ffpopen.toml")
            if "XDG_CONFIG_HOME" in environ
            else Path("~/.config/ffpopen.toml")
        )
    )
    .expanduser()
    .resolve()
)


@dataclass
class Profile:
    name: str
    links: list[str]
    default: bool = False
    active: bool = False

    def open(self, args: list[str]) -> None:
        args = ["firefox", *([] if self.default else ["-P", self.name])] + args
        print(args)
        run(args, check=True)

    def match(self, link: str | None) -> bool:
        return link is not None and any(
            search(link_re, link) is not None for link_re in self.links
        )

    def keys(self, used: set[str] | dict[str, Any]) -> str:
        return next(c for c in self.name.lower() if c not in used and c.isalnum())

    @staticmethod
    def _load_system() -> list["Profile"]:
        profiles_ini = ConfigParser()
        profiles_ini.read(Path("~/.mozilla/firefox/profiles.ini").expanduser())
        profiles: dict[str, Profile] = dict()
        for section in profiles_ini.sections():
            if section.startswith("Profile"):
                profile = Profile(profiles_ini.get(section, "Name"), [])
                profiles[profiles_ini.get(section, "Path")] = profile
            elif section.startswith("Install"):
                if profiles_ini.has_option(section, "Default"):
                    profiles[profiles_ini.get(section, "Default")].default = True
        return list(profiles.values())

    @staticmethod
    def _load_custom() -> list["Profile"]:
        try:
            cfg = toml_loads(PROFILES_PATH.read_text(encoding="locale"))
            return list(map(lambda pd: Profile(**pd), cfg["profile"]))
        except FileNotFoundError:
            return []

    @staticmethod
    def load() -> list["Profile"]:
        merged: dict[str, Profile] = dict()
        for profile in Profile._load_system():
            profile.active = True
            merged[profile.name] = profile
        for profile in Profile._load_custom():
            if profile.name in merged:
                merged[profile.name].links.extend(profile.links)
            else:
                profile.active = False
                merged[profile.name] = profile
        return list(merged.values())


def get_profile_keys(profiles: list[Profile]) -> dict[str, Profile]:
    keys: dict[str, Profile] = {}
    while len(keys) != len(profiles):
        profile = next(profile for profile in profiles if profile not in keys.values())
        try:
            keys[profile.keys(keys)] = profile
        except StopIteration:
            keys = {profile.keys({}): profile}
    return keys


def main() -> None:
    link = argv[-1] if len(argv) > 1 else None
    profiles = get_profile_keys(Profile.load())
    try:
        profile = next(
            profile for _, profile in profiles.items() if profile.match(link)
        )
        profile.open(argv[1:])
    except StopIteration:
        root = Tk(className="ffpopen")
        root.attributes("-topmost", True)
        root.attributes("-type", "utility")
        root.bind_all("<Escape>", lambda _: root.destroy())

        def opener(profile: Profile):
            root.destroy()
            profile.open(argv[1:])

        for key, profile in profiles.items():
            root.bind_all(key, lambda _, p=profile: opener(p))
            Button(
                text=f"{profile.name}{' (default)' if profile.default else ''} [{key}]",
                command=lambda p=profile: opener(p),
                width=20,
            ).pack(fill="x")
        root.wait_window()
