# -*- coding: utf-8 -*-
"""
Created on Sun Mar 22 15:08:48 2020

@author: Omar
"""
import unittest
import sys
import random
sys.path.append("../")
import praw
#Unit
class submissionUnitTest(unittest.TestCase):

    
    def testLogin(self):
        self.reddit=None
        self.username='comp587bot'
        self.appName='comp587testing'
        self.password='thedewthedew69'
        self.personal_use_script='GG6uEHOClfX04g'
        self.client_secret='SAVTrd7SKUMnCV1ZeNLTJLRUoJI'
        #If login works 
        r=praw.Reddit(client_id=self.personal_use_script,
                     client_secret=self.client_secret,
                     user_agent='comp587testing',
                     username=self.username,
                     password='thedewthedew69')
    
    def login(self):
        self.reddit=None
        self.username='comp587bot'
        self.appName='comp587testing'
        self.password='thedewthedew69'
        self.personal_use_script='GG6uEHOClfX04g'
        self.client_secret='SAVTrd7SKUMnCV1ZeNLTJLRUoJI'
        #If login works 
        r=praw.Reddit(client_id=self.personal_use_script,
                     client_secret=self.client_secret,
                     user_agent='comp587testing',
                     username=self.username,
                     password='thedewthedew69')
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
        path_to_image='C:/Users/Omar/Documents/COMP_587/images_for_testing/Capture.PNG'
        subreddit=r.subreddit('comp587testing')
        subreddit.submit_image(title=title,image_path=path_to_image)
        
    def testPostWithVideo(self):
        r=self.login()
        title='First Unit Test with Video'
        path_to_video='C:/Users/Omar/Desktop/bobobo/54.mp4'  
        subreddit=r.subreddit('comp587testing')
        subreddit.submit_video(title=title,video_path=path_to_video)
        
        
#if __name__=='__main__' :
#    teehee=submissionUnitTest()
#    teehee.testPostEmpty()
#    teehee.testPostWithBody()
#    teehee.testPostWithImage()
#    teehee.testPostWithVideo()
#    teehee.testLogin()