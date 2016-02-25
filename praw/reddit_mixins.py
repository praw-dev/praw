"""Provide Reddit Mixin classes."""
import json
import os
from warnings import warn_explicit

import six
from requests.utils import to_native_string

from . import decorators, errors, models
from .const import (JPEG_HEADER, MAX_IMAGE_SIZE, MIN_JPEG_SIZE, MIN_PNG_SIZE,
                    PNG_HEADER)
from .reddits import AuthenticatedReddit


class ModConfigMixin(AuthenticatedReddit):
    """Adds methods requiring the 'modconfig' scope (or mod access).

    You should **not** directly instantiate instances of this class. Use
    :class:`.Reddit` instead.

    """

    @decorators.require_captcha
    def create_subreddit(self, name, title, description='', language='en',
                         subreddit_type='public', content_options='any',
                         over_18=False, default_set=True, show_media=False,
                         domain='', wikimode='disabled', captcha=None,
                         **kwargs):
        """Create a new subreddit.

        :returns: The json response from the server.

        This function may result in a captcha challenge. PRAW will
        automatically prompt you for a response. See :ref:`handling-captchas`
        if you want to manually handle captchas.

        """
        data = {'name': name,
                'title': title,
                'description': description,
                'lang': language,
                'type': subreddit_type,
                'link_type': content_options,
                'over_18': 'on' if over_18 else 'off',
                'allow_top': 'on' if default_set else 'off',
                'show_media': 'on' if show_media else 'off',
                'wikimode': wikimode,
                'domain': domain}
        if captcha:
            data.update(captcha)
        return self.request_json(self.config['site_admin'], data=data)

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

    def get_settings(self, subreddit, **params):
        """Return the settings for the given subreddit."""
        url = self.config['subreddit_settings'].format(
            subreddit=six.text_type(subreddit))
        return self.request_json(url, params=params)['data']

    def set_settings(self, subreddit, title, public_description='',
                     description='', language='en', subreddit_type='public',
                     content_options='any', over_18=False, default_set=True,
                     show_media=False, domain='', domain_css=False,
                     domain_sidebar=False, header_hover_text='',
                     wikimode='disabled', wiki_edit_age=30,
                     wiki_edit_karma=100,
                     submit_link_label='', submit_text_label='',
                     exclude_banned_modqueue=False, comment_score_hide_mins=0,
                     public_traffic=False, collapse_deleted_comments=False,
                     spam_comments='low', spam_links='high',
                     spam_selfposts='high', submit_text='',
                     hide_ads=False, suggested_comment_sort='',
                     key_color='',
                     **kwargs):
        """Set the settings for the given subreddit.

        :param subreddit: Must be a subreddit object.
        :returns: The json response from the server.

        """
        data = {'sr': subreddit.fullname,
                'allow_top': default_set,
                'comment_score_hide_mins': comment_score_hide_mins,
                'collapse_deleted_comments': collapse_deleted_comments,
                'description': description,
                'domain': domain or '',
                'domain_css': domain_css,
                'domain_sidebar': domain_sidebar,
                'exclude_banned_modqueue': exclude_banned_modqueue,
                'header-title': header_hover_text or '',
                'hide_ads': hide_ads,
                'key_color': key_color,
                'lang': language,
                'link_type': content_options,
                'over_18': over_18,
                'public_description': public_description,
                'public_traffic': public_traffic,
                'show_media': show_media,
                'submit_link_label': submit_link_label or '',
                'submit_text': submit_text,
                'submit_text_label': submit_text_label or '',
                'suggested_comment_sort': suggested_comment_sort or '',
                'spam_comments': spam_comments,
                'spam_links': spam_links,
                'spam_selfposts': spam_selfposts,
                'title': title,
                'type': subreddit_type,
                'wiki_edit_age': six.text_type(wiki_edit_age),
                'wiki_edit_karma': six.text_type(wiki_edit_karma),
                'wikimode': wikimode}

        if kwargs:
            msg = 'Extra settings fields: {0}'.format(kwargs.keys())
            warn_explicit(msg, UserWarning, '', 0)
            data.update(kwargs)
        return self.request_json(self.config['site_admin'], data=data)

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

    def update_settings(self, subreddit, **kwargs):
        """Update only the given settings for the given subreddit.

        The settings to update must be given by keyword and match one of the
        parameter names in `set_settings`.

        :returns: The json response from the server.

        """
        settings = self.get_settings(subreddit)
        settings.update(kwargs)
        del settings['subreddit_id']
        return self.set_settings(subreddit, **settings)


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

    def get_flair_list(self, subreddit, *args, **kwargs):
        """Return a get_content generator of flair mappings.

        :param subreddit: Either a Subreddit object or the name of the
            subreddit to return the flair list for.

        The additional parameters are passed directly into
        :meth:`.get_content`. Note: the `url`, `root_field`, `thing_field`, and
        `after_field` parameters cannot be altered.

        """
        url = self.config['flairlist'].format(
            subreddit=six.text_type(subreddit))
        return self.get_content(url, *args, root_field=None,
                                thing_field='users', after_field='next',
                                **kwargs)

    def set_flair(self, subreddit, item, flair_text='', flair_css_class=''):
        """Set flair for the user in the given subreddit.

        `item` can be a string, Redditor object, or Submission object.
        If `item` is a string it will be treated as the name of a Redditor.

        This method can only be called by a subreddit moderator with flair
        permissions. To set flair on yourself or your own links use
        :meth:`~praw.__init__.AuthenticatedReddit.select_flair`.

        :returns: The json response from the server.

        """
        data = {'r': six.text_type(subreddit),
                'text': flair_text or '',
                'css_class': flair_css_class or ''}
        if isinstance(item, models.Submission):
            data['link'] = item.fullname
        else:
            data['name'] = six.text_type(item)
        response = self.request_json(self.config['flair'], data=data)
        return response

    def set_flair_csv(self, subreddit, flair_mapping):
        """Set flair for a group of users in the given subreddit.

        flair_mapping should be a list of dictionaries with the following keys:
          `user`: the user name,
          `flair_text`: the flair text for the user (optional),
          `flair_css_class`: the flair css class for the user (optional)

        :returns: The json response from the server.

        """
        if not flair_mapping:
            raise errors.ClientException('flair_mapping must be set')
        item_order = ['user', 'flair_text', 'flair_css_class']
        lines = []
        for mapping in flair_mapping:
            if 'user' not in mapping:
                raise errors.ClientException('flair_mapping must '
                                             'contain `user` key')
            lines.append(','.join([mapping.get(x, '') for x in item_order]))
        response = []
        while len(lines):
            data = {'r': six.text_type(subreddit),
                    'flair_csv': '\n'.join(lines[:100])}
            response.extend(self.request_json(self.config['flaircsv'],
                                              data=data))
            lines = lines[100:]
        return response


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

    def _get_userlist(self, url, user_only, *args, **kwargs):
        content = self.get_content(url, *args, **kwargs)
        for data in content:
            user = models.Redditor(self, data['name'], fetch=False)
            user.id = data['id'].split('_')[1]
            if user_only:
                yield user
            else:
                data['name'] = user
                yield data

    def get_banned(self, subreddit, user_only=True, *args, **kwargs):
        """Return a get_content generator of banned users for the subreddit.

        :param subreddit: The subreddit to get the banned user list for.
        :param user_only: When False, the generator yields a dictionary of data
            associated with the server response for that user. In such cases,
            the Redditor will be in key 'name' (default: True).

        """
        url = self.config['banned'].format(subreddit=six.text_type(subreddit))
        return self._get_userlist(url, user_only, *args, **kwargs)

    def get_contributors(self, subreddit, *args, **kwargs):
        """
        Return a get_content generator of contributors for the given subreddit.

        If it's a public subreddit, then authentication as a
        moderator of the subreddit is required. For protected/private
        subreddits only access is required. See issue #246.

        """
        def get_contributors_helper(subreddit):
            url = self.config['contributors'].format(
                subreddit=six.text_type(subreddit))
            return self._get_userlist(url, user_only=True, *args, **kwargs)

        if self.is_logged_in():
            if not isinstance(subreddit, models.Subreddit):
                subreddit = self.get_subreddit(subreddit)
            if subreddit.subreddit_type == "public":
                return get_contributors_helper(subreddit)
        return get_contributors_helper(subreddit)

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

    def get_mod_mail(self, subreddit='mod', *args, **kwargs):
        """Return a get_content generator for moderator messages.

        :param subreddit: Either a Subreddit object or the name of the
            subreddit to return the moderator mail from. Defaults to `mod`
            which includes items for all the subreddits you moderate.

        The additional parameters are passed directly into
        :meth:`.get_content`. Note: the `url` parameter cannot be altered.

        """
        url = self.config['mod_mail'].format(
            subreddit=six.text_type(subreddit))
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


class MultiredditMixin(AuthenticatedReddit):
    """Adds methods pertaining to multireddits.

    You should **not** directly instantiate instances of this class. Use
    :class:`.Reddit` instead.

    """

    MULTI_PATH = '/user/{0}/m/{1}'

    def copy_multireddit(self, from_redditor, from_name, to_name=None,
                         *args, **kwargs):
        """Copy a multireddit.

        :param from_redditor: The username or Redditor object for the user
            who owns the original multireddit
        :param from_name: The name of the multireddit, belonging to
            from_redditor
        :param to_name: The name to copy the multireddit as. If None, uses
            the name of the original

        The additional parameters are passed directly into
        :meth:`~praw.__init__.BaseReddit.request_json`

        """
        if to_name is None:
            to_name = from_name

        from_multipath = self.MULTI_PATH.format(from_redditor, from_name)
        to_multipath = self.MULTI_PATH.format(self.user.name, to_name)
        data = {'display_name': to_name,
                'from': from_multipath,
                'to': to_multipath}
        return self.request_json(self.config['multireddit_copy'], data=data,
                                 *args, **kwargs)

    def create_multireddit(self, name, description_md=None, icon_name=None,
                           key_color=None, subreddits=None, visibility=None,
                           weighting_scheme=None, overwrite=False,
                           *args, **kwargs):
        """Create a new multireddit.

        :param name: The name of the new multireddit.
        :param description_md: Optional description for the multireddit,
            formatted in markdown.
        :param icon_name: Optional, choose an icon name from this list: ``art
            and design``, ``ask``, ``books``, ``business``, ``cars``,
            ``comics``, ``cute animals``, ``diy``, ``entertainment``, ``food
            and drink``, ``funny``, ``games``, ``grooming``, ``health``, ``life
            advice``, ``military``, ``models pinup``, ``music``, ``news``,
            ``philosophy``, ``pictures and gifs``, ``science``, ``shopping``,
            ``sports``, ``style``, ``tech``, ``travel``, ``unusual stories``,
            ``video``, or ``None``.
        :param key_color: Optional rgb hex color code of the form `#xxxxxx`.
        :param subreddits: Optional list of subreddit names or Subreddit
            objects to initialize the Multireddit with. You can always
            add more later with
            :meth:`~praw.models.Multireddit.add_subreddit`.
        :param visibility: Choose a privacy setting from this list:
            ``public``, ``private``, ``hidden``. Defaults to private if blank.
        :param weighting_scheme: Choose a weighting scheme from this list:
            ``classic``, ``fresh``. Defaults to classic if blank.
        :param overwrite: Allow for overwriting / updating multireddits.
            If False, and the multi name already exists, throw 409 error.
            If True, and the multi name already exists, use the given
            properties to update that multi.
            If True, and the multi name does not exist, create it normally.

        :returns: The newly created Multireddit object.

        The additional parameters are passed directly into
        :meth:`~praw.__init__.BaseReddit.request_json`

        """
        url = self.config['multireddit_about'].format(user=self.user.name,
                                                      multi=name)
        if subreddits:
            subreddits = [{'name': six.text_type(sr)} for sr in subreddits]
        model = {}
        for key in ('description_md', 'icon_name', 'key_color', 'subreddits',
                    'visibility', 'weighting_scheme'):
            value = locals()[key]
            if value:
                model[key] = value

        method = 'PUT' if overwrite else 'POST'
        return self.request_json(url, data={'model': json.dumps(model)},
                                 method=method, *args, **kwargs)

    def delete_multireddit(self, name, *args, **kwargs):
        """Delete a Multireddit.

        Any additional parameters are passed directly into
        :meth:`~praw.__init__.BaseReddit.request`

        """
        url = self.config['multireddit_about'].format(user=self.user.name,
                                                      multi=name)
        self.http.headers['x-modhash'] = self.modhash
        try:
            self.request(url, data={}, method='DELETE', *args, **kwargs)
        finally:
            del self.http.headers['x-modhash']

    def edit_multireddit(self, *args, **kwargs):
        """Edit a multireddit, or create one if it doesn't already exist.

        See :meth:`create_multireddit` for accepted parameters.

        """
        return self.create_multireddit(*args, overwrite=True, **kwargs)

    def get_multireddit(self, redditor, multi, *args, **kwargs):
        """Return a Multireddit object for the author and name specified.

        :param redditor: The username or Redditor object of the user
            who owns the multireddit.
        :param multi: The name of the multireddit to fetch.

        The additional parameters are passed directly into the
        :class:`.Multireddit` constructor.

        """
        return models.Multireddit(self, six.text_type(redditor), multi,
                                  *args, **kwargs)

    def get_multireddits(self, redditor, *args, **kwargs):
        """Return a list of multireddits belonging to a redditor.

        :param redditor: The username or Redditor object to find multireddits
            from.
        :returns: The json response from the server

        The additional parameters are passed directly into
        :meth:`~praw.__init__.BaseReddit.request_json`

        If the requested redditor is the current user, all multireddits
        are visible. Otherwise, only public multireddits are returned.

        """
        redditor = six.text_type(redditor)
        url = self.config['multireddit_user'].format(user=redditor)
        return self.request_json(url, *args, **kwargs)

    def rename_multireddit(self, current_name, new_name, *args, **kwargs):
        """Rename a Multireddit.

        :param current_name: The name of the multireddit to rename
        :param new_name: The new name to assign to this multireddit

        The additional parameters are passed directly into
        :meth:`~praw.__init__.BaseReddit.request_json`

        """
        current_path = self.MULTI_PATH.format(self.user.name, current_name)
        new_path = self.MULTI_PATH.format(self.user.name, new_name)
        data = {'from': current_path,
                'to': new_path}
        return self.request_json(self.config['multireddit_rename'], data=data,
                                 *args, **kwargs)


class MySubredditsMixin(AuthenticatedReddit):
    """Adds methods requiring the 'mysubreddits' scope (or login).

    You should **not** directly instantiate instances of this class. Use
    :class:`.Reddit` instead.

    """

    def get_my_contributions(self, *args, **kwargs):
        """Return a get_content generator of subreddits.

        The Subreddits generated are those where the session's user is a
        contributor.

        The additional parameters are passed directly into
        :meth:`.get_content`. Note: the `url` parameter cannot be altered.

        """
        return self.get_content(self.config['my_con_subreddits'], *args,
                                **kwargs)

    def get_my_moderation(self, *args, **kwargs):
        """Return a get_content generator of subreddits.

        The Subreddits generated are those where the session's user is a
        moderator.

        The additional parameters are passed directly into
        :meth:`.get_content`. Note: the `url` parameter cannot be altered.

        """
        return self.get_content(self.config['my_mod_subreddits'], *args,
                                **kwargs)

    def get_my_multireddits(self):
        """Return a list of the authenticated Redditor's Multireddits."""
        # The JSON data for multireddits is returned from Reddit as a list
        # Therefore, we cannot use :meth:`get_content` to retrieve the objects
        return self.request_json(self.config['my_multis'])

    def get_my_subreddits(self, *args, **kwargs):
        """Return a get_content generator of subreddits.

        The subreddits generated are those that hat the session's user is
        subscribed to.

        The additional parameters are passed directly into
        :meth:`.get_content`. Note: the `url` parameter cannot be altered.

        """
        return self.get_content(self.config['my_subreddits'], *args, **kwargs)


class PrivateMessagesMixin(AuthenticatedReddit):
    """Adds methods requiring the 'privatemessages' scope (or login).

    You should **not** directly instantiate instances of this class. Use
    :class:`.Reddit` instead.

    """

    def _mark_as_read(self, thing_ids, unread=False):
        """Mark each of the supplied thing_ids as (un)read.

        :returns: The json response from the server.

        """
        data = {'id': ','.join(thing_ids)}
        key = 'unread_message' if unread else 'read_message'
        response = self.request_json(self.config[key], data=data)
        return response

    def get_comment_replies(self, *args, **kwargs):
        """Return a get_content generator for inboxed comment replies.

        The additional parameters are passed directly into
        :meth:`.get_content`. Note: the `url` parameter cannot be altered.

        """
        return self.get_content(self.config['comment_replies'],
                                *args, **kwargs)

    def get_inbox(self, *args, **kwargs):
        """Return a get_content generator for inbox (messages and comments).

        The additional parameters are passed directly into
        :meth:`.get_content`. Note: the `url` parameter cannot be altered.

        """
        return self.get_content(self.config['inbox'], *args, **kwargs)

    def get_message(self, message_id, *args, **kwargs):
        """Return a Message object corresponding to the given ID.

        :param message_id: The ID or Fullname for a Message

        The additional parameters are passed directly into
        :meth:`~praw.models.Message.from_id` of Message, and subsequently into
        :meth:`.request_json`.

        """
        return models.Message.from_id(self, message_id, *args, **kwargs)

    def get_messages(self, *args, **kwargs):
        """Return a get_content generator for inbox (messages only).

        The additional parameters are passed directly into
        :meth:`.get_content`. Note: the `url` parameter cannot be altered.

        """
        return self.get_content(self.config['messages'], *args, **kwargs)

    def get_post_replies(self, *args, **kwargs):
        """Return a get_content generator for inboxed submission replies.

        The additional parameters are passed directly into
        :meth:`.get_content`. Note: the `url` parameter cannot be altered.

        """
        return self.get_content(self.config['post_replies'], *args, **kwargs)

    def get_sent(self, *args, **kwargs):
        """Return a get_content generator for sent messages.

        The additional parameters are passed directly into
        :meth:`.get_content`. Note: the `url` parameter cannot be altered.

        """
        return self.get_content(self.config['sent'], *args, **kwargs)

    def get_unread(self, unset_has_mail=False, update_user=False, *args,
                   **kwargs):
        """Return a get_content generator for unread messages.

        :param unset_has_mail: When True, clear the has_mail flag (orangered)
            for the user.
        :param update_user: If both `unset_has_mail` and `update user` is True,
            set the `has_mail` attribute of the logged-in user to False.

        The additional parameters are passed directly into
        :meth:`.get_content`. Note: the `url` parameter cannot be altered.

        """
        params = kwargs.setdefault('params', {})
        if unset_has_mail:
            params['mark'] = 'true'
            if update_user:  # Update the user object
                setattr(self.user, 'has_mail', False)
        return self.get_content(self.config['unread'], *args, **kwargs)

    def get_mentions(self, *args, **kwargs):
        """Return a get_content generator for username mentions.

        The additional parameters are passed directly into
        :meth:`.get_content`. Note: the `url` parameter cannot be altered.

        """
        return self.get_content(self.config['mentions'], *args, **kwargs)

    @decorators.require_captcha
    def send_message(self, recipient, subject, message, from_sr=None,
                     captcha=None, **kwargs):
        """Send a message to a redditor or a subreddit's moderators (mod mail).

        :param recipient: A Redditor or Subreddit instance to send a message
            to. A string can also be used in which case the string is treated
            as a redditor unless it is prefixed with either '/r/' or '#', in
            which case it will be treated as a subreddit.
        :param subject: The subject of the message to send.
        :param message: The actual message content.
        :param from_sr: A Subreddit instance or string to send the message
            from. When provided, messages are sent from the subreddit rather
            than from the authenticated user. Note that the authenticated user
            must be a moderator of the subreddit and have mail permissions.

        :returns: The json response from the server.

        This function may result in a captcha challenge. PRAW will
        automatically prompt you for a response. See :ref:`handling-captchas`
        if you want to manually handle captchas.

        """
        if isinstance(recipient, models.Subreddit):
            recipient = '/r/{0}'.format(six.text_type(recipient))
        else:
            recipient = six.text_type(recipient)

        data = {'text': message,
                'subject': subject,
                'to': recipient}
        if from_sr:
            data['from_sr'] = six.text_type(from_sr)
        if captcha:
            data.update(captcha)
        response = self.request_json(self.config['compose'], data=data,
                                     retry_on_error=False)
        return response


class ReportMixin(AuthenticatedReddit):
    """Adds methods requiring the 'report' scope (or login).

    You should **not** directly instantiate instances of this class. Use
    :class:`.Reddit` instead.

    """

    def hide(self, thing_id, _unhide=False):
        """Hide up to 50 objects in the context of the logged in user.

        :param thing_id: A single fullname or list of fullnames,
            representing objects which will be hidden.
        :param _unhide: If True, unhide the object(s) instead.  Use
            :meth:`~praw.__init__.ReportMixin.unhide` rather than setting this
            manually.

        :returns: The json response from the server.

        """
        if not isinstance(thing_id, six.string_types):
            thing_id = ','.join(thing_id)
        method = 'unhide' if _unhide else 'hide'
        data = {'id': thing_id,
                'executed': method}
        return self.request_json(self.config[method], data=data)

    def unhide(self, thing_id):
        """Unhide up to 50 objects in the context of the logged in user.

        :param thing_id: A single fullname or list of fullnames,
            representing objects which will be unhidden.

        :returns: The json response from the server.

        """
        return self.hide(thing_id, _unhide=True)


class SubmitMixin(AuthenticatedReddit):
    """Adds methods requiring the 'submit' scope (or login).

    You should **not** directly instantiate instances of this class. Use
    :class:`.Reddit` instead.

    """

    def _add_comment(self, thing_id, text):
        """Comment on the given thing with the given text.

        :returns: A Comment object for the newly created comment.

        """
        data = {'thing_id': thing_id, 'text': text}
        retval = self.request_json(self.config['comment'], data=data,
                                   retry_on_error=False)
        return retval['data']['things'][0]

    @decorators.require_captcha
    def submit(self, subreddit, title, text=None, url=None, captcha=None,
               save=None, send_replies=None, resubmit=None, **kwargs):
        """Submit a new link to the given subreddit.

        Accepts either a Subreddit object or a str containing the subreddit's
        display name.

        :param resubmit: If True, submit the link even if it has already been
            submitted.
        :param save: If True the new Submission will be saved after creation.
        :param send_replies: If True, inbox replies will be received when
            people comment on the submission. If set to None, the default of
            True for text posts and False for link posts will be used.

        :returns: The newly created Submission object if the reddit instance
            can access it. Otherwise, return the url to the submission.

        This function may result in a captcha challenge. PRAW will
        automatically prompt you for a response. See :ref:`handling-captchas`
        if you want to manually handle captchas.

        """
        if isinstance(text, six.string_types) == bool(url):
            raise TypeError('One (and only one) of text or url is required!')
        data = {'sr': six.text_type(subreddit),
                'title': title}
        if text or text == '':
            data['kind'] = 'self'
            data['text'] = text
        else:
            data['kind'] = 'link'
            data['url'] = url
        if captcha:
            data.update(captcha)
        if resubmit is not None:
            data['resubmit'] = resubmit
        if save is not None:
            data['save'] = save
        if send_replies is not None:
            data['sendreplies'] = send_replies
        result = self.request_json(self.config['submit'], data=data,
                                   retry_on_error=False)
        url = result['data']['url']
        try:
            return self.get_submission(url)
        except errors.Forbidden:
            # While the user may be able to submit to a subreddit,
            # that does not guarantee they have read access.
            return url


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


class Reddit(ModConfigMixin, ModFlairMixin, ModLogMixin, ModOnlyMixin,
             ModSelfMixin, MultiredditMixin, MySubredditsMixin,
             PrivateMessagesMixin, ReportMixin, SubmitMixin, SubscribeMixin):
    """Provides access to reddit's API.

    See :class:`.BaseReddit`'s documentation for descriptions of the
    initialization parameters.

    """
