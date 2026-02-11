from herald.targets import MastodonTarget, TelegramTarget
from herald.targets.base import FakeTarget
from herald.targets.dryrun import DryRunTarget

target_registry = {
    "mastodon": MastodonTarget,
    "dryrun": DryRunTarget,
    "telegram": TelegramTarget,
    "faketarget": FakeTarget,
}
