"""Provide the GildableMixin class."""
from six import text_type


class GildableMixin(object):
    """Interface for classes that can be gilded."""

    def gild(self, months=None):
        """Gild the Redditor or author of the content.

        :param months: Specifies the number of months to gild. This parameter
            is Only valid when the instance called upon is of type
            Redditor. When not provided, the value defaults to 1.
        :returns: True on success, otherwise raises an exception.

        """
        from ..redditor import Redditor
        if isinstance(self, Redditor):
            months = int(months) if months is not None else 1
            if months < 1:
                raise TypeError('months must be at least 1')
            if months > 36:
                raise TypeError('months must be no more than 36')
            response = self.reddit_session.post(
                self.reddit_session.config['gild_user'].format(
                    username=text_type(self)), data={'months': months})
        elif months is not None:
            raise TypeError('months is not a valid parameter for {0}'
                            .format(type(self)))
        else:
            response = self.reddit_session.post(
                self.reddit_session.config['gild_thing']
                .format(fullname=self.fullname))
        return response.status_code == 200
