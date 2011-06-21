#!python2.6
# Copyright 2011.  BSpoke, LLC. 

__author__ = 'Matt Maeda <msmaeda@gmail.com>'

import unittest

from app import urlfetcher

class UrlFetcherTest(unittest.TestCase):
    """Unit tests of the url fetcher."""

    def setUp(self):
        self.app            = urlfetcher

    def testValidDescriptions(self):
        """ Test that valid descriptions return true """
        self.assertTrue(self.app._ignore_jobs(""))
        self.assertTrue(self.app._ignore_jobs("This is valid"))
        self.assertTrue(self.app._ignore_jobs("you can telecommute"))
        
    def testInvalidDescriptions(self):
        """ Test that invalid descriptions return false """
        self.assertFalse(self.app._ignore_jobs("telecommuting is not an option"))
        self.assertFalse(self.app._ignore_jobs("No telecommuting"))
        self.assertFalse(self.app._ignore_jobs("No telecommute"))
        self.assertFalse(self.app._ignore_jobs("TELECOMMUTE IS NOT AN OPTION"))            
            
    def testTagJobs(self):
        """ Test that tags are properly applied """
        self.assertTrue("C#" in self.app._tag_jobs("C#"))
        self.assertTrue("C++" in self.app._tag_jobs("c++"))
        self.assertTrue("Objective C" in self.app._tag_jobs("obj-c"))
        self.assertTrue(".NET" in self.app._tag_jobs(".NET"))
        self.assertEqual(0, len(self.app._tag_jobs("random text to see")))
        
        
        
        
