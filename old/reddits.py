"""Contains old code for reference."""

r"""
    def get_domain_listing(self, domain, sort='hot', period=None, *args,
                           **kwargs):

        Corresponds to the submissions provided by
        ``https://www.reddit.com/domain/{domain}``.

        :param domain: The domain to generate a submission listing for.
        :param sort: When provided must be one of 'hot', 'new', 'rising',
            'controversial, or 'top'. Defaults to 'hot'.
        :param period: When sort is either 'controversial', or 'top' the period
            can be either None (for account default), 'all', 'year', 'month',
            'week', 'day', or 'hour'.

        The additional parameters are passed directly into
        :meth:`.get_content`. Note: the `url` parameter cannot be altered.

        # Verify arguments
        if sort not in ('controversial', 'hot', 'new', 'rising', 'top'):
            raise TypeError('Invalid sort parameter.')
        if period not in (None, 'all', 'day', 'hour', 'month', 'week', 'year'):
            raise TypeError('Invalid period parameter.')
        if sort not in ('controversial', 'top') and period:
            raise TypeError('Period cannot be set for that sort argument.')

        url = self.config['domain'].format(domain=domain)
        if sort != 'hot':
            url += sort
        if period:  # Set or overwrite params 't' parameter
            kwargs.setdefault('params', {})['t'] = period
        return self.get_content(url, *args, **kwargs)

    def get_flair(self, subreddit, redditor, **params):
        :param subreddit: Can be either a Subreddit object or the name of a
            subreddit.
        :param redditor: Can be either a Redditor object or the name of a
            redditor.
        :returns: None if the user doesn't exist, otherwise a dictionary
            containing the keys `flair_css_class`, `flair_text`, and `user`.
        name = six.text_type(redditor)
        params.update(name=name)
        url = self.config['flairlist'].format(
            subreddit=six.text_type(subreddit))
        data = self.request_json(url, params=params)
        if not data['users'] or \
                data['users'][0]['user'].lower() != name.lower():
            return None
        return data['users'][0]

    def get_info(self, url=None, thing_id=None, limit=None):
        :param url: The url to lookup.
        :param thing_id: A single thing_id, or a list of thing_ids. A thing_id
            can be any one of Comment (``t1_``), Link (``t3_``), or Subreddit
            (``t5_``) to lookup by fullname.
        :param limit: The maximum number of Submissions to return when looking
            up by url. When None, uses account default settings.
        :returns: When a single ``thing_id`` is provided, return the
            corresponding thing object, or ``None`` if not found. When a list
            of ``thing_id``s or a ``url`` is provided return a list of thing
            objects (up to ``limit``). ``None`` is returned if any one of the
            thing_ids or the URL is invalid.

        if bool(url) == bool(thing_id):
            raise TypeError('Only one of url or thing_id is required!')
        elif thing_id and limit:
            raise TypeError('Limit keyword is not applicable with thing_id.')
        if url:
            params = {'url': url}
            if limit:
                params['limit'] = limit
        else:
            if not isinstance(thing_id, six.string_types):
                thing_id = ','.join(thing_id)
                url = True  # Enable returning a list
            params = {'id': thing_id}
        items = self.request_json(self.config['info'],
                                  params=params)['data']['children']
        if url:
            return items if items else None
        elif items:
            return items[0]
        else:
            return None

    def get_moderators(self, subreddit, **kwargs):
        url = self.config['moderators'].format(
            subreddit=six.text_type(subreddit))
        return self.request_json(url, **kwargs)

    def get_submissions(self, fullnames, *args, **kwargs):
        Generate Submission objects for each item provided in `fullnames`.

        A submission fullname looks like `t3_<base36_id>`. Submissions are
        yielded in the same order they appear in `fullnames`.

        Up to 100 items are batched at a time -- this happens transparently.

        The additional parameters are passed directly into
        :meth:`.get_content`. Note: the `url` and `limit` parameters cannot be
        altered.
        fullnames = fullnames[:]
        while fullnames:
            cur = fullnames[:100]
            fullnames[:100] = []
            url = self.config['by_id'] + ','.join(cur)
            for item in self.get_content(url, limit=len(cur), *args, **kwargs):
                yield item

    def get_subreddit_recommendations(self, subreddits, omit=None):
        Return a list of recommended subreddits as Subreddit objects.

        Subreddits with activity less than a certain threshold, will not have
        any recommendations due to lack of data.

        :param subreddits: A list of subreddits (either names or Subreddit
            objects) to base the recommendations on.
        :param omit: A list of subreddits (either names or Subreddit
            objects) that will be filtered out of the result.
        params = {'omit': _to_reddit_list(omit or [])}
        url = self.config['sub_recommendations'].format(
            subreddits=_to_reddit_list(subreddits))
        result = self.request_json(url, params=params)
        return [models.Subreddit(self, sub['sr_name']) for sub in result]

    def get_traffic(self, subreddit):
        Return the json dictionary containing traffic stats for a subreddit.

        :param subreddit: The subreddit whose /about/traffic page we will
            collect.
        url = self.config['subreddit_traffic'].format(
            subreddit=six.text_type(subreddit))
        return self.request_json(url)

    def get_wiki_page(self, subreddit, page):
        Return a WikiPage object for the subreddit and page provided.
        return models.WikiPage(self, six.text_type(subreddit), page.lower())

    def get_wiki_pages(self, subreddit):
        Return a list of WikiPage objects for the subreddit.
        url = self.config['wiki_pages'].format(
            subreddit=six.text_type(subreddit))
        return self.request_json(url)

    def is_username_available(self, username):
        Return True if username is valid and available, otherwise False.
        params = {'user': username}
        try:
            result = self.request_json(self.config['username_available'],
                                       params=params)
        except errors.BadUsername:
            return False
        return result

    def accept_moderator_invite(self, subreddit):
        Accept a moderator invite to the given subreddit.

        Callable upon an instance of Subreddit with no arguments.

        :returns: The json response from the server.
        data = {'r': six.text_type(subreddit)}
        # Clear moderated subreddits and cache
        return self.request_json(self.config['accept_mod_invite'], data=data)

    def delete(self, password, message=""):
        Delete the currently authenticated redditor.

        WARNING!

        This action is IRREVERSIBLE. Use only if you're okay with NEVER
        accessing this reddit account again.

        :param password: password for currently authenticated account
        :param message: optional 'reason for deletion' message.
        :returns: json response from the server.
        data = {'user': self.user.name,
                'passwd': password,
                'delete_message': message,
                'confirm': True}
        return self.request_json(self.config['delete_redditor'], data=data)

    def edit_wiki_page(self, subreddit, page, content, reason=''):
        Create or edit a wiki page with title `page` for `subreddit`.

        :returns: The json response from the server.
        data = {'content': content,
                'page': page,
                'r': six.text_type(subreddit),
                'reason': reason}
        return self.request_json(self.config['wiki_edit'], data=data)

    def get_flair_choices(self, subreddit, link=None):
        Return available flair choices and current flair.

        :param link: If link is given, return the flair options for this
            submission. Not normally given directly, but instead set by calling
            the flair_choices method for Submission objects.
            Use the default for the session's user.

        :returns: A dictionary with 2 keys. 'current' containing current flair
            settings for the authenticated user and 'choices' containing a list
            of possible flair choices.
        data = {'r':  six.text_type(subreddit), 'link': link}
        return self.request_json(self.config['flairselector'], data=data)

    def select_flair(self, item, flair_template_id='', flair_text=''):
        Select user flair or link flair on subreddits.

        This can only be used for assigning your own name flair or link flair
        on your own submissions. For assigning other's flairs using moderator
        access, see :meth:`~praw.__init__.ModFlairMixin.set_flair`.

        :param item: A string, Subreddit object (for user flair), or
            Submission object (for link flair). If ``item`` is a string it
            will be treated as the name of a Subreddit.
        :param flair_template_id: The id for the desired flair template. Use
            the :meth:`~praw.models.Subreddit.get_flair_choices` and
            :meth:`~praw.models.Submission.get_flair_choices` methods to find
            the ids for the available user and link flair choices.
        :param flair_text: A string containing the custom flair text.
            Used on subreddits that allow it.

        :returns: The json response from the server.
        data = {'flair_template_id': flair_template_id or '',
                'text':              flair_text or ''}
        if isinstance(item, models.Submission):  # Link flair
            data['link'] = item.fullname
        else:  # User flair

            data['name'] = self.user.name
            data['r'] = six.text_type(item)
        response = self.request_json(self.config['select_flair'], data=data)
        return response
"""
