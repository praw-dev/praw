import praw 
import yaml
import sys
import urllib.request #for generating words 
import random 
sys.path.append("../")

class automatedTesting(): 

    def login(self):
        login_doc='../credentials.yaml'
        with open(login_doc,'r') as stream:
            credentials=yaml.load(stream)
        self.reddit=None
        self.username=credentials['username']
        self.appName=credentials['user_agent']
        self.subreddit=credentials['subreddit']
        self.password=credentials['password']
        self.personal_use_script=credentials['personal_use_script']
        self.client_secret=credentials['client_secret']
        #If login works 
        r = praw.Reddit(client_id=self.personal_use_script,
                     client_secret=self.client_secret,
                     user_agent=self.appName,
                     username=self.username,
                     password=self.password)
        return r

    # Tests single post submission
    def testPost(self):
        r = self.login()
        title = self.randomTitleGenerator()
        body = self.randomBodyGenerator()
        subreddit = r.subreddit('comp587testing')
        subreddit.submit(title=title, selftext=body)

    # Test multiple post submissions from 1 to 10 
    def testMultiplePostings(self): 
        post = 0
        randompost = self.randomInts(1, 10)
        while (post < randompost): 
            r = self.login()
            title = self.randomTitleGenerator()
            body = self.randomBodyGenerator()
            subreddit = r.subreddit('comp587testing')
            subreddit.submit(title=title, selftext=body)
            post += 1

    # Generates Random Title for post 
    def randomTitleGenerator(self): 
        # Get list of words from web
        word_url = "http://svnweb.freebsd.org/csrg/share/dict/words?view=co&content-type=text/plain"
        response = urllib.request.urlopen(word_url)
        long_txt = response.read().decode()
        words = long_txt.splitlines()

        title = " "
        index = 0
        randomsize = self.randomInts(1, 10)
        
        # Make random title of appended words 
        while (index < randomsize):
            randomword = self.randomInts(0, len(words) - 1)
            title = title + " " + words[randomword]
            index += 1

        print(title)

        return title

    # Generates random bodies ranged from 0 to api bound
    def randomBodyGenerator(self): 
        # Get list of words from web
        word_url = "http://svnweb.freebsd.org/csrg/share/dict/words?view=co&content-type=text/plain"
        response = urllib.request.urlopen(word_url)
        long_txt = response.read().decode()
        words = long_txt.splitlines()

        body = " "
        index = 0
        randomsize = self.randomInts(0, 100)
        print(randomsize)
        while (index < randomsize):
            randomword = self.randomInts(0, len(words) - 1)
            body = body + " " + words[randomword]
            index += 1

        return body

    # generates random integers 
    def randomInts(self, minlength, maxlength):
        rand = random.randint(minlength, maxlength)
        return rand



if __name__ == "__main__":
    # instance 
    autotest = automatedTesting()
    autotest.testMultiplePostings()

