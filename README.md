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
window:
  before: "24h"                  # required: end of window (e.g. 30m, 12h, 7d)
  after: "0m"                    # optional: start of window (default: now)

targets:
  - type: mastodon
    template: templates/mastodon.txt
    publish_mode: single    # optional (default: grouped)
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

Example for a shifted window (from now+3 days to now+5 days):

```yaml
window:
  after: "3d"
  before: "5d"
```

## Templates

Templates use [Jinja2](https://jinja.palletsprojects.com/) syntax. The available variables depend on the `publish_mode` setting.

### `grouped` mode (default)

All events are published in a single post.

**Context variables:**

| Variable | Type | Description                                                        |
|---|---|--------------------------------------------------------------------|
| `events` | list | [Event](./src/herald/domain/event.py) objects sorted by start time |
| `count` | int | Number of events                                                   |
| `today` | datetime | Current datetime                                                   |

**Example template:**
```jinja
Events for {{ today | datefmt }}

{% for event in events %}
{{ event.start | datefmt }}: {{ event.title }} ({{ event.location }})
{% endfor %}
```

### `single` mode

Each event is published as its own post.

**Context variables:**

| Variable | Type | Description                                                        |
|---|---|--------------------------------------------------------------------|
| `event` | Event | A single [Event](./src/herald/domain/event.py) object             |
| `today` | datetime | Current datetime                                                   |

**Example template:**

```jinja
{{ event.start | datefmt }}: {{ event.title }}
{% if event.location %}Location: {{ event.location }}{% endif %}
```

### Template filters
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
