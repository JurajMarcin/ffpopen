# ffp-open

Open links using a selected Firefox Profile.

`ffp-open LINK` parses available Firefox profiles from
`~/.mozilla/firefox/profiles.ini` a lets the user choose which profile they
want to open `LINK` with.

## Configuration

Configuration is loaded from `$FFPOPEN_PROFILES` or
`$XDG_CONFIG_HOME/ffpopen.toml` or `~/.config/ffpopen.toml`.

Profiles can be assigned regex expressions, matching links are automatically
opened with that profile. Links are matched using Python `re.search()`, you can
use `^` and `$` to match the whole link only.

```toml
[[profile]]
name = "Personal"
links = ['discord\.com']

[[profile]]
name = "default-release"
links = ['gitlab\.com']
```
