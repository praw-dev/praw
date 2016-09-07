from mock import MagicMock
from functools import wraps
from json import dumps
from requests.structures import CaseInsensitiveDict


class MockResponse(MagicMock):
    """Mock a response.

    This provides an object to mock a response given a real response and values
    that want to be changed. All attributes passed have priority over the real
    responses, which are used as a fallback, except when it comes to headers.
    With headers, any headers that are not set are taken from the real
    response if they exist. This is to ensure there won't be inconsistencies
    with the necessary headers.

    Recommended usage is as follows:

    1. Record the request(s) that need to be mocked via the betamax() factory
        decorator in helper.py

    2. Pass pass_recorder=True to betamax() and add a recorder argument to the
        test function

    3. The responses that you may wish to mock are available as the
        'recorded_response' attribute on the recorder's current cassette
        interaction. It's easiest to determine the interaction that you
        will need to mock via a debugger.

    The request content is determined from it's json, which is given as a
    dictionary/list. This is because all reddit api responses are valid json.
    If you must, you can set the text attribute as well, but this is only used
    if json is None.

    You can use the `as_context` method to use a context manager, or
    `as_decorator` to use this as a decorator and pass the mocked response as
    an extra argument.

    """
    def __init__(self, real_response, status_code=None, json=None,
                 raise_for_status=None, close=None, reason=None, cookies=None,
                 apparent_encoding=None, encoding=None, history=None,
                 headers=None, elapsed=None, _content_consumed=None,
                 parent=None, text=None, **kwargs):
        super(MockResponse, self).__init__(spec=real_response)
        self.real_response = real_response
        self.apparent_encoding = apparent_encoding or \
            real_response.apparent_encoding
        self.close = close or real_response.close
        self.json = (lambda: json) if json else real_response.json
        self.text = dumps(self.json()) if json else text
        self._content_consumed = _content_consumed or \
            real_response._content_consumed
        self.content = self.text.encode()
        self.parent = parent
        for k, v in kwargs.items():
            setattr(self, k, v)
        self._content = self.content
        self.history = history if history else \
            ([] or real_response.history)
        self.elapsed = elapsed if elapsed else \
            (type(real_response.elapsed)() or real_response.elapsed)
        self.cookies = cookies if cookies else \
            (type(real_response.cookies)() or real_response.cookies)
        self.encoding = encoding or real_response.encoding
        self.iter_content = iter(self.content)
        self.iter_lines = iter([self.content])
        self.raise_for_status = raise_for_status or \
            real_response.raise_for_status
        self.raw = real_response.raw
        self.status_code = status_code or real_response.status_code
        self.headers = CaseInsensitiveDict(headers) if headers else \
            CaseInsensitiveDict()
        for name, val in real_response.headers.items():
            self.headers.setdefault(name, val)
        self.reason = reason or real_response.reason
        self.is_permanent_redirect = \
            ('location' in self.headers and self.status_code in [301, 308])
        self.ok = 200 <= self.status_code < 300

    @classmethod
    def in_place(cls, holder, attribute='recorded_response',
                 *args, **kwargs):
        setattr(holder, attribute, cls(getattr(holder, attribute),
                                       *args, **kwargs))

    @classmethod
    def as_context(cls, holder, attribute='recorded_response',
                   *args, **kwargs):
        class in_context(object):
            def __init__(self, holder, attribute, *args, **kwargs):
                self.holder, self.attribute, self.args, self.kwargs = \
                    holder, attribute, args, kwargs

            def __enter__(self):
                cls.in_place(self.holder, self.attribute, *self.args,
                             **self.kwargs)
                return getattr(self.holder, self.attribute)

            def __exit__(self, exc_type, exc_val, exc_trace):
                setattr(self.holder, self.attribute,
                        getattr(self.holder, self.attribute).real_response)
        return in_context(holder, attribute, *args, **kwargs)

    @classmethod
    def as_decorator(cls, holder, attribute='recorded_response',
                     *args, **kwargs):
        def factory(func):
            @wraps(func)
            def wrapped(*a, **kw):
                with cls.as_context(holder, attribute,
                                    *args, **kwargs) as resp:
                    a = list(a)
                    a.append(resp)
                    a = tuple(a)
                    return func(*a, **kw)
            return wrapped
        return factory
