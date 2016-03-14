"""
Decorators.

They mainly do two things: ensure API guidelines are followed and
prevent unnecessary failed API requests by testing that the call can be made
first. Also, they can limit the length of output strings and parse json
response for certain errors.
"""

import sys
from warnings import warn

import decorator
from six.moves.urllib.parse import urljoin  # pylint: disable=import-error

from . import errors


def _get_captcha(reddit_session, captcha_id):
    """Prompt user for captcha solution and return a prepared result."""
    url = urljoin(reddit_session.config['captcha'],
                  captcha_id + '.png')
    sys.stdout.write('Captcha URL: {0}\nCaptcha: '.format(url))
    sys.stdout.flush()
    raw = sys.stdin.readline()
    if not raw:  # stdin has reached the end of file
        # Trigger exception raising next time through. The request is
        # cached so this will not require and extra request and delay.
        sys.stdin.close()
        return None
    return {'iden': captcha_id, 'captcha': raw.strip()}


def deprecated(msg=''):
    """Deprecate decorated method."""
    @decorator.decorator
    def wrap(function, *args, **kwargs):
        if not kwargs.pop('disable_warning', False):
            warn(msg, DeprecationWarning)
        return function(*args, **kwargs)
    return wrap


@decorator.decorator
def raise_api_exceptions(function, *args, **kwargs):
    """Raise client side exception(s) when present in the API response.

    Returned data is not modified.

    """
    try:
        return_value = function(*args, **kwargs)
    except errors.HTTPException as exc:
        if exc._raw.status_code != 400:
            raise  # Unhandled HTTPErrors
        try:  # Attempt to convert v1 errors into older format (for now)
            data = exc._raw.json()
            assert len(data) == 2
            return_value = {'errors': [(data['reason'],
                                        data['explanation'], '')]}
        except Exception:
            raise exc
    if isinstance(return_value, dict):
        if return_value.get('error') == 304:  # Not modified exception
            raise errors.NotModified(return_value)
        elif return_value.get('errors'):
            error_list = []
            for error_type, msg, value in return_value['errors']:
                if error_type in errors.ERROR_MAPPING:
                    error_class = errors.ERROR_MAPPING[error_type]
                else:
                    error_class = errors.APIException
                error_list.append(error_class(error_type, msg, value,
                                              return_value))
            if len(error_list) == 1:
                raise error_list[0]
            else:
                raise errors.ExceptionList(error_list)
    return return_value


@decorator.decorator
def require_captcha(function, *args, **kwargs):
    """Return a decorator for methods that require captchas."""
    raise_captcha_exception = kwargs.pop('raise_captcha_exception', False)
    captcha_id = None

    # Get a handle to the reddit session
    if hasattr(args[0], 'reddit_session'):
        reddit_session = args[0].reddit_session
    else:
        reddit_session = args[0]

    while True:
        try:
            if captcha_id:
                captcha_answer = _get_captcha(reddit_session, captcha_id)

                func_args = []
                if 'captcha' in func_args:
                    captcha_index = func_args.index('captcha')
                    args = list(args)
                    args[captcha_index] = captcha_answer
                else:
                    kwargs['captcha'] = captcha_answer
            return function(*args, **kwargs)
        except errors.InvalidCaptcha as exception:
            if raise_captcha_exception or \
                    not hasattr(sys.stdin, 'closed') or sys.stdin.closed:
                raise
            captcha_id = exception.response['captcha']
