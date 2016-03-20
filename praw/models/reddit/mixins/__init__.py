"""Package providing reddit class mixins."""
from .editable import EditableMixin  # NOQA
from .gildable import GildableMixin  # NOQA
from .inboxable import InboxableMixin  # NOQA
from .messageable import MessageableMixin  # NOQA
from .moderatable import ModeratableMixin  # NOQA
from .replyable import ReplyableMixin  # NOQA
from .reportable import ReportableMixin  # NOQA
from .savable import SavableMixin  # NOQA
from .votable import VotableMixin  # NOQA


class UserContentMixin(EditableMixin, GildableMixin, ModeratableMixin,
                       ReplyableMixin, ReportableMixin, SavableMixin,
                       VotableMixin):
    """A convenience mixin that applies to both Comments and Submissions."""
