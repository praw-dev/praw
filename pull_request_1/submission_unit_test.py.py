
import unittest
import sys
import random
sys.path.append("../")
import praw
#Unit
class submissionUnitTest(unittest.TestCase):

    
    def testLogin(self):
        self.reddit=None
        self.username=''
        self.appName=''
        self.password=''
        self.personal_use_script=''
        self.client_secret=''
        #If login works 
        r=praw.Reddit(client_id=self.personal_use_script,
                     client_secret=self.client_secret,
                     user_agent='',
                     username=self.username,
                     password='')
    
    def login(self):
        self.reddit=None
        self.username=''
        self.appName=''
        self.password=''
        self.personal_use_script=''
        self.client_secret=''
        #If login works 
        r=praw.Reddit(client_id=self.personal_use_script,
                     client_secret=self.client_secret,
                     user_agent='',
                     username=self.username,
                     password='')
        return r
    
    def testPostEmpty(self):
        r=self.login()
        title="First Unit Test"
        body=''
        subreddit=r.subreddit('comp587testing')
        subreddit.submit(title=title,selftext=body)
        
    def testPostWithBody(self):
        r=self.login()
        title="Second Unit Test"
        body='This is the body'
        subreddit=r.subreddit('comp587testing')
        subreddit.submit(title=title,selftext=body)        
        
    def testPostWithImage(self):
        r=self.login()
        title='First Unit Test with Image'
        path_to_image=''
        subreddit=r.subreddit('comp587testing')
        subreddit.submit_image(title=title,image_path=path_to_image)
        
    def testPostWithVideo(self):
        r=self.login()
        title='First Unit Test with Video'
        path_to_video=''  
        subreddit=r.subreddit('comp587testing')
        subreddit.submit_video(title=title,video_path=path_to_video)
        
        
#if __name__=='__main__' :
#    teehee=submissionUnitTest()
#    teehee.testPostEmpty()
#    teehee.testPostWithBody()
#    teehee.testPostWithImage()
#    teehee.testPostWithVideo()
#    teehee.testLogin()