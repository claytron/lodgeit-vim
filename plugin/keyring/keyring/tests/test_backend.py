"""
test_backend.py

Test case for keyring basic function

created by Kang Zhang 2009-07-14
"""


import random
import unittest
import string
import os
import sys
import commands
import keyring.backend

from keyring.backend import PasswordSetError

ALPHABET = string.ascii_letters + string.digits
DIFFICULT_CHARS = string.whitespace + string.punctuation

def random_string(k, source = ALPHABET):
    """Generate a random string with length <i>k</i>
    """
    result = ''
    for i in range(0, k):
        result += random.choice(source)
    return result

def backup(file):
    """Backup the file as file.bak
    """
    commands.getoutput( "mv %s{,.bak}" % file )

def restore(file):
    """Restore the file from file.bak
    """
    commands.getoutput( "mv %s{.bak,}" % file )

class BackendBasicTestCase(unittest.TestCase):
    """Test for the keyring's basic funtions. password_set and password_get
    """

    __test__ = False

    def init_keyring(self):
        return None

    def setUp(self):
        self.keyring = self.init_keyring()

    def check_set_get(self, service, username, password):
        keyring = self.keyring

        if self.supported() == -1: # skip the unsupported keyring
            return

        # for the non-exsit password
        self.assertEqual(keyring.get_password(service, username), None)

        # common usage
        keyring.set_password(service, username, password)
        self.assertEqual(keyring.get_password(service, username), password)

        # for the empty password
        keyring.set_password(service, username, "")
        self.assertEqual(keyring.get_password(service, username), "")

    def test_password_set_get(self):
        password = random_string(20)
        username = random_string(20)
        service = random_string(20)
        self.check_set_get(service, username, password)

    def test_difficult_chars(self):
        password = random_string(20, DIFFICULT_CHARS)
        username = random_string(20, DIFFICULT_CHARS)
        service = random_string(20, DIFFICULT_CHARS)
        self.check_set_get(service, username, password)

    def supported(self):
        """Return the correct value for supported.
        """
        return -1

    def test_supported(self):
        """Test the keyring's supported value.
        """
        self.assertEqual(self.keyring.supported(), self.supported())

class OSXKeychainTestCase(BackendBasicTestCase):
    __test__ = True

    def init_keyring(self):
        print >> sys.stderr, "Testing OSXKeychain, following password prompts are for this keyring"
        return keyring.backend.OSXKeychain()

    def supported(self):
        if sys.platform in ('mac','darwin'):
            return 1
        return -1

class GnomeKeyringTestCase(BackendBasicTestCase):
    __test__ = True

    def init_keyring(self):
        print >> sys.stderr, "Testing GnomeKeyring, following password prompts are for this keyring"
        return keyring.backend.GnomeKeyring()

    def supported(self):
        try:
            import gnome_keyring
        except ImportError:
            return -1
        if os.getenv("GNOME_DESKTOP_SESSION_ID") is not None:
            return 1
        return 0

class KDEKWalletTestCase(BackendBasicTestCase):
    __test__ = True

    def init_keyring(self):
        print >> sys.stderr, "Testing KDEKWallet, following password prompts are for this keyring"
        return keyring.backend.KDEKWallet()

    def supported(self):
        try:
            import kde_kwallet
        except ImportError:
            return -1
        if os.getenv("KDE_FULL_SESSION") == "true":
            return 1
        return 0

class FileKeyringTestCase(BackendBasicTestCase):
    __test__ = False

    def setUp(self):
        """Backup the file before the test
        """
        self.keyring = self.init_keyring()

        self.file_path = os.path.join(os.path.expanduser("~"),
                                                       self.keyring.filename())
        backup(self.file_path)

    def tearDown(self):
        """Restore the keyring file.
        """
        restore(self.file_path)

    def test_encrypt_decrypt(self):
        if self.supported() == -1: # skip the unsupported platform
            return

        password = random_string(20)
        encyrpted = self.keyring.encrypt(password)

        self.assertEqual(password, self.keyring.decrypt(encyrpted))

class UncryptedFileKeyringTestCase(FileKeyringTestCase):
    __test__ = True

    def init_keyring(self):
        print >> sys.stderr, "Testing UnecryptedFile, following password prompts are for this keyring"
        return keyring.backend.UncryptedFileKeyring()

    def supported(self):
        return 0

class CryptedFileKeyringTestCase(FileKeyringTestCase):
    __test__ = True

    def init_keyring(self):
        print >> sys.stderr, "Testing CryptedFile, following password prompts are for this keyring"
        return keyring.backend.CryptedFileKeyring()

    def supported(self):
        try:
            from Crypto.Cipher import AES
            return 0
        except ImportError:
            pass
        return -1

class Win32CryptoKeyringTestCase(FileKeyringTestCase):
    __test__ = True

    def init_keyring(self):
        print >> sys.stderr, "Testing Win32, following password prompts are for this keyring"
        return keyring.backend.Win32CryptoKeyring()

    def supported(self):
        try:
            import win32_crypto
            if sys.platform in ['win32'] and sys.getwindowsversion()[-2] == 2:
                return 1
        except ImportError:
            pass
        return -1

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(OSXKeychainTestCase))
    suite.addTest(unittest.makeSuite(GnomeKeyringTestCase))
    suite.addTest(unittest.makeSuite(KDEKWalletTestCase))
    suite.addTest(unittest.makeSuite(UncryptedFileKeyringTestCase))
    suite.addTest(unittest.makeSuite(CryptedFileKeyringTestCase))
    suite.addTest(unittest.makeSuite(Win32CryptoKeyringTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest="test_suite")
