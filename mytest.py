import unittest 
import server

class URLTestCase(unittest.TestCase):
    def setUp(self):

        self.ex = 5

    def tearDown(self):
        self.ex = 0


    def test_base_url_ending_with_slash_allowed(self):
        self.assertEqual( server.resolve( './www/' ), './www/' )

    def test_base_url_not_ending_with_slash_allowed(self):
        self.assertEqual( server.resolve( './www' ), './www' )

    def test_file_in_base_url_allowed(self):
        self.assertEqual( server.resolve( './www/base.html' ), './www/base.html' )

    def test_file_in_base_folder_ending_with_slash_allowed(self):
        self.assertEqual( server.resolve( './www/folder/' ), './www/folder/' )

    def test_file_in_base_folder_not_ending_with_slash_allowed(self):
        self.assertEqual( server.resolve( './www/folder' ), './www/folder' )

    def test_file_outside_web_domain1(self):
        self.assertEqual( server.resolve('./www/../../../../../etc/group'), './www/etc/group' )

    def test_file_outside_web_domain2(self):
        self.assertEqual( server.resolve('./www/../../../folder1/folder2/base.css'), './www/folder1/folder2/base.css' )

    def test_looping_outside_web_domain(self):
        self.assertEqual( server.resolve('./www/../www/../www/../www/base.css'), './www/www/base.css' )

    def test_looping_within_web_domain1(self):
        self.assertEqual( server.resolve('./www/folder1/../folder2/../folder2/../base.css'), './www/base.css' )

    def test_looping_within_web_domain2(self):
        self.assertEqual( server.resolve('./www/folder1/folder2/../folder2/folder3/../../folder2/folder3/base.css'), './www/folder1/folder2/folder3/base.css' )


class HTTPRequestTestCase(unittest.TestCase):
    def test_ex(self):
        self.assertTrue( True )


class HTTPResponseTestCase(unittest.TestCase):
    def test_ex(self):
        self.assertTrue( True )


if __name__ == "__main__":
    unittest.main()