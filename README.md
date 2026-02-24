# Herald
Publish upcoming events from your `.ics` calendar to WhatsApp, Mastodon, and other platforms. 

## Installation
```
pip install git+https://github.com/Debakel/herald.git
```

## Usage

```bash
herald --config config.yaml              # publish events
herald --config config.yaml --dry-run    # preview without publishing
```

## Configuration

```yaml
source: "/path/to/calendar.ics"  # or https://example.com/calendar.ics
lookahead_window: "24h"          # how far ahead to look (e.g. 30m, 12h, 7d)

targets:
  - type: mastodon
    template: templates/mastodon.txt
    post_mode: single    # optional (default: grouped; also: single)
    config:
      instance_url: "https://mastodon.social"
      client_id: "..."
      client_secret: "..."
      access_token: "..."

  - type: telegram
    template: templates/telegram.txt
    config:
      bot_token: "..."
      chat_id: "..."
      parse_mode: "HTML"  # optional (default: HTML; also: Markdown, MarkdownV2)
```

## Templates

Templates use [Jinja2](https://jinja.palletsprojects.com/) syntax. The available variables depend on the `post_mode` setting.

### `grouped` mode (default)

All events are published in a single post.

```jinja
Events for {{ today | datefmt }}

{% for event in events %}
{{ event.start | datefmt }}: {{ event.title }} ({{ event.location }})
{% endfor %}
```

| Variable | Type | Description                                                        |
|---|---|--------------------------------------------------------------------|
| `events` | list | [Event](./src/herald/domain/event.py) objects sorted by start time |
| `count` | int | Number of events                                                   |
| `today` | datetime | Current datetime                                                   |

### `single` mode

Each event is published as its own post.

```jinja
{{ event.start | datefmt }}: {{ event.title }}
{% if event.location %}Location: {{ event.location }}{% endif %}
```

| Variable | Type | Description                                                        |
|---|---|--------------------------------------------------------------------|
| `event` | Event | A single [Event](./src/herald/domain/event.py) object             |
| `today` | datetime | Current datetime                                                   |

**Template filters:**
- `datefmt` formats a datetime using Babel locale formatting.

## Deployment

```cron
# Post daily at 7:00 AM
0 7 * * * /usr/local/bin/herald --config /etc/herald/config.yaml
```

## Development

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync --all-groups   # install dependencies
uv run pytest          # run tests
```
