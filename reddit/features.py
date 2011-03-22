from decorators import require_login

class Saveable(object):
    """
    Additional interface for Reddit content objects that can be saved.
    Currently only Submissions, but this may change at a later date, as
    eventually Comments will probably end up being saveable.
    """
    @require_login
    def save(self, unsave=False):
        """If logged in, save the content specified by `content_id`."""
        url = urls["unsave" if unsave else "save"]
        params = {'id': self.name,
                  'executed': "unsaved" if unsave else "saved",
                  'uh': self.reddit_session.modhash}
        response = self.reddit_session._request_json(url, params)
        _request.is_stale(urls.saved_links)

    def unsave(self):
        return self.save(unsave=True)
        
class Deletable(object):
    """
    Additional Interface for Reddit content objects that can be deleted
    (currently Submission and Comment).
    """
    def delete(self):
        url = urls["del"]
        params = {'id' : self.name,
                    'executed' : 'deleted',  
                    'r' : self.subreddit, 
                    'uh' : self.reddit_session.modhash}
        return self.reddit_session._request_json(url, params)

class Voteable(object):
    """
    Additional interface for Reddit content objects that can be voted on
    (currently Submission and Comment).
    """
    @require_login
    def vote(self, direction=0):
        """
        Vote for the given content_id in the direction specified.
        """
        url = urls["vote"]
        params = {'id' : self.name,
                  'dir' : direction,
                  'r' : self.subreddit,
                  'uh' : self.reddit_session.modhash}
        return self.reddit_session._request_json(url, params)

    def upvote(self):
        return self.vote(direction=1)

    def downvote(self):
        return self.vote(direction=-1)

