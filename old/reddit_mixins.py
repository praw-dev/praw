"""Provide Reddit Mixin classes."""
import json
import os

import six
from requests.utils import to_native_string

from . import errors, models
from .const import (JPEG_HEADER, MAX_IMAGE_SIZE, MIN_JPEG_SIZE, MIN_PNG_SIZE,
                    PNG_HEADER)
from .reddits import AuthenticatedReddit


class ModConfigMixin(AuthenticatedReddit):
    """Adds methods requiring the 'modconfig' scope (or mod access).

    You should **not** directly instantiate instances of this class. Use
    :class:`.Reddit` instead.

    """

    def delete_image(self, subreddit, name=None, header=False):
        """Delete an image from the subreddit.

        :param name: The name of the image if removing a CSS image.
        :param header: When true, delete the subreddit header.
        :returns: The json response from the server.

        """
        subreddit = six.text_type(subreddit)
        if name and header:
            raise TypeError('Both name and header cannot be set.')
        elif name:
            data = {'img_name': name}
            url = self.config['delete_sr_image']
        else:
            data = True
            url = self.config['delete_sr_header']
        url = url.format(subreddit=subreddit)
        return self.request_json(url, data=data)

    def set_stylesheet(self, subreddit, stylesheet):
        """Set stylesheet for the given subreddit.

        :returns: The json response from the server.

        """
        subreddit = six.text_type(subreddit)
        data = {'r': subreddit,
                'stylesheet_contents': stylesheet,
                'op': 'save'}  # Options: save / preview
        return self.request_json(self.config['subreddit_css'], data=data)

    def upload_image(self, subreddit, image_path, name=None, header=False):
        """Upload an image to the subreddit.

        :param image_path: A path to the jpg or png image you want to upload.
        :param name: The name to provide the image. When None the name will be
            filename less any extension.
        :param header: When True, upload the image as the subreddit header.
        :returns: A link to the uploaded image. Raises an exception otherwise.

        """
        if name and header:
            raise TypeError('Both name and header cannot be set.')
        image_type = None
        # Verify image is a jpeg or png and meets size requirements
        with open(image_path, 'rb') as image:
            size = os.path.getsize(image.name)
            if size < MIN_PNG_SIZE:
                raise errors.ClientException('png image is too small.')
            if size > MAX_IMAGE_SIZE:
                raise errors.ClientException('`image` is too big. Max: {0} '
                                             'bytes'.format(MAX_IMAGE_SIZE))
            first_bytes = image.read(MIN_PNG_SIZE)
            image.seek(0)
            if first_bytes.startswith(PNG_HEADER):
                image_type = 'png'
            elif first_bytes.startswith(JPEG_HEADER):
                if size < MIN_JPEG_SIZE:
                    raise errors.ClientException('jpeg image is too small.')
                image_type = 'jpg'
            else:
                raise errors.ClientException('`image` must be either jpg or '
                                             'png.')
            data = {'r': six.text_type(subreddit), 'img_type': image_type}
            if header:
                data['header'] = 1
            else:
                if not name:
                    name = os.path.splitext(os.path.basename(image.name))[0]
                data['name'] = name

            response = json.loads(self._request(
                self.config['upload_image'], data=data, files={'file': image},
                method=to_native_string('POST'), retry_on_error=False))

        if response['errors']:
            raise errors.APIException(response['errors'], None)
        return response['img_src']


class ModFlairMixin(AuthenticatedReddit):
    """Adds methods requiring the 'modflair' scope (or mod access).

    You should **not** directly instantiate instances of this class. Use
    :class:`.Reddit` instead.

    """

    def add_flair_template(self, subreddit, text='', css_class='',
                           text_editable=False, is_link=False):
        """Add a flair template to the given subreddit.

        :returns: The json response from the server.

        """
        data = {'r': six.text_type(subreddit),
                'text': text,
                'css_class': css_class,
                'text_editable': six.text_type(text_editable),
                'flair_type': 'LINK_FLAIR' if is_link else 'USER_FLAIR'}
        return self.request_json(self.config['flairtemplate'], data=data)

    def clear_flair_templates(self, subreddit, is_link=False):
        """Clear flair templates for the given subreddit.

        :returns: The json response from the server.

        """
        data = {'r': six.text_type(subreddit),
                'flair_type': 'LINK_FLAIR' if is_link else 'USER_FLAIR'}
        return self.request_json(self.config['clearflairtemplates'], data=data)

    def configure_flair(self, subreddit, flair_enabled=False,
                        flair_position='right',
                        flair_self_assign=False,
                        link_flair_enabled=False,
                        link_flair_position='left',
                        link_flair_self_assign=False):
        """Configure the flair setting for the given subreddit.

        :returns: The json response from the server.

        """
        flair_enabled = 'on' if flair_enabled else 'off'
        flair_self_assign = 'on' if flair_self_assign else 'off'
        if not link_flair_enabled:
            link_flair_position = ''
        link_flair_self_assign = 'on' if link_flair_self_assign else 'off'
        data = {'r': six.text_type(subreddit),
                'flair_enabled': flair_enabled,
                'flair_position': flair_position,
                'flair_self_assign_enabled': flair_self_assign,
                'link_flair_position': link_flair_position,
                'link_flair_self_assign_enabled': link_flair_self_assign}
        return self.request_json(self.config['flairconfig'], data=data)

    def delete_flair(self, subreddit, user):
        """Delete the flair for the given user on the given subreddit.

        :returns: The json response from the server.

        """
        data = {'r': six.text_type(subreddit),
                'name': six.text_type(user)}
        return self.request_json(self.config['deleteflair'], data=data)


class ModLogMixin(AuthenticatedReddit):
    """Adds methods requiring the 'modlog' scope (or mod access).

    You should **not** directly instantiate instances of this class. Use
    :class:`.Reddit` instead.

    """

    def get_mod_log(self, subreddit, mod=None, action=None, *args, **kwargs):
        """Return a get_content generator for moderation log items.

        :param subreddit: Either a Subreddit object or the name of the
            subreddit to return the modlog for.
        :param mod: If given, only return the actions made by this moderator.
            Both a moderator name or Redditor object can be used here.
        :param action: If given, only return entries for the specified action.

        The additional parameters are passed directly into
        :meth:`.get_content`. Note: the `url` parameter cannot be altered.

        """
        params = kwargs.setdefault('params', {})
        if mod is not None:
            params['mod'] = six.text_type(mod)
        if action is not None:
            params['type'] = six.text_type(action)
        url = self.config['modlog'].format(subreddit=six.text_type(subreddit))
        return self.get_content(url, *args, **kwargs)


class ModOnlyMixin(AuthenticatedReddit):
    """Adds methods requiring the logged in moderator access.

    You should **not** directly instantiate instances of this class. Use
    :class:`.Reddit` instead.

    """

    def get_banned(self, subreddit, user_only=True, *args, **kwargs):
        """Return a get_content generator of banned users for the subreddit.

        :param subreddit: The subreddit to get the banned user list for.
        :param user_only: When False, the generator yields a dictionary of data
            associated with the server response for that user. In such cases,
            the Redditor will be in key 'name' (default: True).

        """
        url = self.config['banned'].format(subreddit=six.text_type(subreddit))
        return self._get_userlist(url, user_only, *args, **kwargs)

    def get_edited(self, subreddit='mod', *args, **kwargs):
        """Return a get_content generator of edited items.

        :param subreddit: Either a Subreddit object or the name of the
            subreddit to return the edited items for. Defaults to `mod` which
            includes items for all the subreddits you moderate.

        The additional parameters are passed directly into
        :meth:`.get_content`. Note: the `url` parameter cannot be altered.

        """
        url = self.config['edited'].format(subreddit=six.text_type(subreddit))
        return self.get_content(url, *args, **kwargs)

    def get_mod_queue(self, subreddit='mod', *args, **kwargs):
        """Return a get_content generator for the moderator queue.

        :param subreddit: Either a Subreddit object or the name of the
            subreddit to return the modqueue for. Defaults to `mod` which
            includes items for all the subreddits you moderate.

        The additional parameters are passed directly into
        :meth:`.get_content`. Note: the `url` parameter cannot be altered.

        """
        url = self.config['modqueue'].format(
            subreddit=six.text_type(subreddit))
        return self.get_content(url, *args, **kwargs)

    def get_muted(self, subreddit, user_only=True, *args, **kwargs):
        """Return a get_content generator for modmail-muted users.

        :param subreddit: Either a Subreddit object or the name of a subreddit
            to get the list of muted users from.

        The additional parameters are passed directly into
        :meth:`.get_content`. Note: the `url` parameter cannot be altered.

        """
        url = self.config['muted'].format(subreddit=six.text_type(subreddit))
        return self._get_userlist(url, user_only, *args, **kwargs)

    def get_reports(self, subreddit='mod', *args, **kwargs):
        """Return a get_content generator of reported items.

        :param subreddit: Either a Subreddit object or the name of the
            subreddit to return the reported items. Defaults to `mod` which
            includes items for all the subreddits you moderate.

        The additional parameters are passed directly into
        :meth:`.get_content`. Note: the `url` parameter cannot be altered.

        """
        url = self.config['reports'].format(subreddit=six.text_type(subreddit))
        return self.get_content(url, *args, **kwargs)

    def get_spam(self, subreddit='mod', *args, **kwargs):
        """Return a get_content generator of spam-filtered items.

        :param subreddit: Either a Subreddit object or the name of the
            subreddit to return the spam-filtered items for. Defaults to `mod`
            which includes items for all the subreddits you moderate.

        The additional parameters are passed directly into
        :meth:`.get_content`. Note: the `url` parameter cannot be altered.

        """
        url = self.config['spam'].format(subreddit=six.text_type(subreddit))
        return self.get_content(url, *args, **kwargs)

    def get_stylesheet(self, subreddit, **params):
        """Return the stylesheet and images for the given subreddit."""
        url = self.config['stylesheet'].format(
            subreddit=six.text_type(subreddit))
        return self.request_json(url, params=params)['data']

    def get_unmoderated(self, subreddit='mod', *args, **kwargs):
        """Return a get_content generator of unmoderated submissions.

        :param subreddit: Either a Subreddit object or the name of the
            subreddit to return the unmoderated submissions for. Defaults to
            `mod` which includes items for all the subreddits you moderate.

        The additional parameters are passed directly into
        :meth:`.get_content`. Note: the `url` parameter cannot be altered.

        """
        url = self.config['unmoderated'].format(
            subreddit=six.text_type(subreddit))
        return self.get_content(url, *args, **kwargs)

    def get_wiki_banned(self, subreddit, *args, **kwargs):
        """Return a get_content generator of users banned from the wiki."""
        url = self.config['wiki_banned'].format(
            subreddit=six.text_type(subreddit))
        return self._get_userlist(url, user_only=True, *args, **kwargs)

    def get_wiki_contributors(self, subreddit, *args, **kwargs):
        """Return a get_content generator of wiki contributors.

        The returned users are those who have been approved as a wiki
        contributor by the moderators of the subreddit, Whether or not they've
        actually contributed to the wiki is irrellevant, their approval as wiki
        contributors is all that matters.

        """
        url = self.config['wiki_contributors'].format(
            subreddit=six.text_type(subreddit))
        return self._get_userlist(url, user_only=True, *args, **kwargs)


class ModSelfMixin(AuthenticatedReddit):
    """Adds methods pertaining to the 'modself' OAuth scope (or login).

    You should **not** directly instantiate instances of this class. Use
    :class:`.Reddit` instead.

    """

    def leave_contributor(self, subreddit):
        """Abdicate approved submitter status in a subreddit. Use with care.

        :param subreddit: The name of the subreddit to leave `status` from.

        :returns: the json response from the server.
        """
        return self._leave_status(subreddit, self.config['leavecontributor'])

    def leave_moderator(self, subreddit):
        """Abdicate moderator status in a subreddit. Use with care.

        :param subreddit: The name of the subreddit to leave `status` from.

        :returns: the json response from the server.
        """
        return self._leave_status(subreddit, self.config['leavemoderator'])

    def _leave_status(self, subreddit, statusurl):
        """Abdicate status in a subreddit.

        :param subreddit: The name of the subreddit to leave `status` from.
        :param statusurl: The API URL which will be used in the leave request.
            Please use :meth:`leave_contributor` or :meth:`leave_moderator`
            rather than setting this directly.

        :returns: the json response from the server.
        """
        if isinstance(subreddit, six.string_types):
            subreddit = self.get_subreddit(subreddit)

        data = {'id': subreddit.fullname}
        return self.request_json(statusurl, data=data)


class PrivateMessagesMixin(AuthenticatedReddit):
    """Adds methods requiring the 'privatemessages' scope (or login).

    You should **not** directly instantiate instances of this class. Use
    :class:`.Reddit` instead.

    """

    def get_message(self, message_id, *args, **kwargs):
        """Return a Message object corresponding to the given ID.

        :param message_id: The ID or Fullname for a Message

        The additional parameters are passed directly into
        :meth:`~praw.models.Message.from_id` of Message, and subsequently into
        :meth:`.request_json`.

        """
        return models.Message.from_id(self, message_id, *args, **kwargs)

    def get_mentions(self, *args, **kwargs):
        """Return a get_content generator for username mentions.

        The additional parameters are passed directly into
        :meth:`.get_content`. Note: the `url` parameter cannot be altered.

        """
        return self.get_content(self.config['mentions'], *args, **kwargs)


class SubscribeMixin(AuthenticatedReddit):
    """Adds methods requiring the 'subscribe' scope (or login).

    You should **not** directly instantiate instances of this class. Use
    :class:`.Reddit` instead.

    """

    def subscribe(self, subreddit, unsubscribe=False):
        """Subscribe to the given subreddit.

        :param subreddit: Either the subreddit name or a subreddit object.
        :param unsubscribe: When True, unsubscribe.
        :returns: The json response from the server.

        """
        data = {'action': 'unsub' if unsubscribe else 'sub',
                'sr_name': six.text_type(subreddit)}
        return self.request_json(self.config['subscribe'], data=data)

    def unsubscribe(self, subreddit):
        """Unsubscribe from the given subreddit.

        :param subreddit: Either the subreddit name or a subreddit object.
        :returns: The json response from the server.

        """
        return self.subscribe(subreddit, unsubscribe=True)
