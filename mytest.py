import unittest 
import server

class URLTestCase(unittest.TestCase):
    def setUp(self):

        self.ex = 5

    def tearDown(self):
        self.ex = 0


    def test_base_url_ending_with_slash_allowed(self):
        self.assertTrue( server.isURLWithinWebDomain( './www/' ) )

    def test_base_url_not_ending_with_slash_allowed(self):
        self.assertTrue( server.isURLWithinWebDomain( './www' ) )

    def test_file_in_base_url_allowed(self):
        self.assertTrue( server.isURLWithinWebDomain( './www/base.html' ) )

    def test_file_in_base_folder_ending_with_slash_allowed(self):
        self.assertTrue( server.isURLWithinWebDomain( './www/folder/' ) )

    def test_file_in_base_folder_not_ending_with_slash_allowed(self):
        self.assertTrue( server.isURLWithinWebDomain( './www/folder' ) )

    def test_file_outside_web_domain1(self):
        self.assertFalse( server.isURLWithinWebDomain('./www/../../../../../etc/group') )

    def test_file_outside_web_domain2(self):
        self.assertFalse( server.isURLWithinWebDomain('./www/../../../folder1/folder2/base.css') )

    def test_looping_outside_web_domain(self):
        self.assertTrue( server.isURLWithinWebDomain('./www/../www/../www/../www/base.css') )


class HTTPRequestTestCase(unittest.TestCase):
    def test_ex(self):
        self.assertTrue( True )


class HTTPResponseTestCase(unittest.TestCase):
    def test_ex(self):
        self.assertTrue( True )


if __name__ == "__main__":
    unittest.main()