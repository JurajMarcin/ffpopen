# ffpopen

Open links using a selected Firefox Profile.

`ffpopen [ARGS ...]` parses available Firefox profiles from
`~/.mozilla/firefox/profiles.ini` a lets you choose which Firefox profile you
want to use. `ffpopen` then launches Firefox with
`firefox -P <profile> [ARGS ...]`.

`ffpopen` provides a `.desktop` file which you can select as your default
browser using XDG/DM Settings/...

## Configuration

Configuration is loaded from one of the following paths (after first success,
the rest is ignored):
- `$FFPOPEN_PROFILES`
- `$XDG_CONFIG_HOME/ffpopen.toml`
- `~/.config/ffpopen.toml`.

Profiles can be assigned regex expressions, matching links are automatically
opened with that profile. Links are matched using Python's `re.search()`, you can
use `^` and `$` to match the start or end of the URL

```toml
[[profile]]
name = "personal"
links = ['local\.home']

[[profile]]
name = "work"
links = ['gitlab\.com']
```
