import curses
import hashlib
import binascii

from ethereum_bip44.crypto import HDPrivateKey, HDKey
from base64 import b64encode, b64decode
from base58 import b58encode

from ecdsa import SECP256k1, numbertheory
from pywallet.pywallet import wallet

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


def new_encrypted_account(username, password):
    # creates a new account and encrypts all info
    seed = generate_seed()
    return encrypt_seed(username, password, seed)


def generate_seed():
    # generates a 12 word mnemonic seed
    seed = wallet.generate_mnemonic()
    if output_seed(seed):
        return seed
    return generate_seed()


def output_seed(seed):
    #  displays seed and clears screen afterwards
    stdscr = curses.initscr()
    stdscr.keypad(True)
    curses.noecho()
    str1 = "| A new mnemonic seed phrase has been created. You will need the seed to restore your account.          " \
           "   |\n"
    str2 = "| Please store OFFLINE and in order presented. " \
           "Anyone with access to your seed has access to your accounts.|\n"
    border = (len(str2) - 1) * "*" + "\n"
    try:
        stdscr.addstr(border + str1 + str2 + border)
        stdscr.addstr("Press 'enter' to view your seed phrase.\n\n")
        stdscr.getch()
        stdscr.addstr(seed.upper())
        stdscr.addstr("\n\nPress 'enter' to continue.")
        stdscr.getch()
        exit_stdscr(stdscr)
    except KeyboardInterrupt:  #  People probably gonna try to copy the seed
        exit_stdscr(stdscr)
        return False
    if seed_confirmation(seed):  #  Ensures user has accurately stored seed. New seed until confirmation
        return True
    return False


def seed_confirmation(seed):
    # asks user to type seed in again to verify it was stored accurately. Clears screen afterwards
    stdscr = curses.initscr()
    curses.echo()
    for x in range(3, 0, -1):
        stdscr.addstr("Please enter your seed for confirmation. Space between words is necessary (not case sensitive)")
        stdscr.addstr(f"\n{x} attempts left\nSeed: ")
        confirm_seed = stdscr.getstr().decode('ascii')
        if seed.lower() == confirm_seed.lower():
            exit_stdscr(stdscr)
            return True
        stdscr.clear()
        stdscr.addstr("The seed phrases do not match!\n")
    exit_stdscr(stdscr)
    return False


def encrypt_seed(username, password, seed):
    # encrypts the seed for storage using the username and password
    encryption_key = md5_digest(username + password)
    cipher = AES.new(encryption_key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(str.encode(seed), AES.block_size))
    iv = b64encode(cipher.iv).decode('utf-8')
    ct = b64encode(ct_bytes).decode('utf-8')
    return iv + " " + ct


def decrypt_seed(decryption_key, iv, encrypted_seed):
    # decrypts seed for use
    try:
        iv = b64decode(iv)
        encrypted_seed = b64decode(encrypted_seed)
        cipher = AES.new(decryption_key, AES.MODE_CBC, iv)
        decrypted_key = unpad(cipher.decrypt(encrypted_seed), AES.block_size)
        return decrypted_key
    except ValueError or KeyError:
        return False


def verify_password(username, password, iv, encrypted_seed):
    # verifies password of associated account is correct
    decryption_key = md5_digest(username + password)
    return decrypt_seed(decryption_key, iv, encrypted_seed)


def sha256_hex(unhashed_str):
    # return sha256 hash of str in hex form
    hasher = hashlib.sha256()
    hasher.update(str.encode(unhashed_str))
    return hasher.hexdigest()


def md5_digest(unhashed_str):
    # return md5 hash of str in bytes form
    hasher = hashlib.md5()
    hasher.update(str.encode(unhashed_str))
    return hasher.digest()


def rmd160(unhashed_bytes):
    # return rmd160 hash of bytes in hex form
    hasher = hashlib.new('ripemd160')
    hasher.update(unhashed_bytes)
    return hasher.hexdigest()


def decode_generated_eth_key(pkey_hex):
    pkey = HDPrivateKey.from_hex(pkey_hex)
    keys = HDKey.from_path(pkey, '{change}/{index}'.format(change=0, index=0))
    private_key = keys[-1]
    return private_key._key.to_hex()


def exit_stdscr(stdscr):
    # clears and exit curses window
    stdscr.clear()
    curses.endwin()


class EOSPoint(object):
    """
    Modification of Point class from ecdsa.ellipticcurve to match Point class implementation of EOSJS.
    """

    def __init__(self,
                 curve=SECP256k1.curve,
                 x=SECP256k1.generator.x(),
                 y=SECP256k1.generator.y(),
                 z=1,
                 order=None):
        """curve, x, y, z, order; order (optional) is the order of this point."""
        self.__curve = curve
        self.__x = x
        self.__y = y
        self.__z = z
        self.__order = order
        # self.curve is allowed to be None only for INFINITY:

    def __add__(self, other):
        """Add one point to another point."""

        if other == INFINITY:
            return self
        if self == INFINITY:
            return other
        assert self.__curve == other.__curve

        x1 = self.__x
        y1 = self.__y
        z1 = self.__z
        x2 = other.__x
        y2 = other.__y
        z2 = other.__z
        p = self.__curve.p()

        u = ((y2 * z1) - (y1 * z2)) % p
        v = ((x2 * z1) - (x1 * z2)) % p

        if v == 0:
            if u == 0:
                return self.double()
            return INFINITY

        x3 = (v * (z2 * ((z1 * u**2) - (2 * x1 * v**2)) - v**3)) % p
        y3 = (z2 * ((3 * x1 * u * v**2) - (y1 * v**3) - (z1 * u**3)) + (u * v**3)) % p
        z3 = (v**3 * z1 * z2) % p

        return EOSPoint(self.__curve, x=x3, y=y3, z=z3)

    def __mul__(self, other):
        """Multiply a point by an integer."""
        def leftmost_bit(x):
            assert x > 0
            result = 1
            while result <= x:
                result = 2 * result
            return result // 2

        e = other
        if self.__order:
            e = e % self.__order
        if e == 0:
            return INFINITY
        if self == INFINITY:
            return INFINITY
        assert e > 0

        p = self.__curve.p()
        e3 = 3 * e
        negative_self = EOSPoint(self.__curve, self.__x, p-self.__y, self.__z, self.__order)
        i = leftmost_bit(e3) // 2
        result = self
        # print_("Multiplying %s by %d (e3 = %d):" % (self, other, e3))

        while i > 1:
            result = result.double()
            if (e3 & i) != 0 and (e & i) == 0:
                result = result + self
            if (e3 & i) == 0 and (e & i) != 0:
                result = result + negative_self
            # print_(". . . i = %d, result = %s" % ( i, result ))
            i = i // 2

        return result

    def __rmul__(self, other):
        """Multiply a point by an integer."""
        return self * other

    def __str__(self):
        if self == INFINITY:
            return "infinity"
        return f"{hex(self.x())}, {hex(self.y())}, {hex(self.z())}"

    def double(self):
        """Return a new point that is twice the old."""
        if self == INFINITY:
            return INFINITY

        p = self.__curve.p()
        a = self.__curve.a()
        x1 = self.__x
        y1 = self.__y
        z1 = self.__z

        w = ((3 * x1**2) + (a * z1**2)) % p

        x3 = (2 * y1 * z1 * (w**2 - (8 * x1 * y1**2 * z1))) % p
        y3 = ((4 * y1**2 * z1 * ((3 * w * x1) - (2 * y1**2 * z1))) - w**3) % p
        z3 = (8 * (y1 * z1)**3) % p

        return EOSPoint(self.__curve, x=x3, y=y3, z=z3)

    def affineX(self):
        # affine transform of point x
        p = self.__curve.p()
        Zinv = numbertheory.inverse_mod(self.__z, p)
        return (self.__x * Zinv) % p

    def affineY(self):
        # affine transform of point x
        p = self.__curve.p()
        Zinv = numbertheory.inverse_mod(self.__z, p)
        return (self.__y * Zinv) % p

    def to_public_key(self):
        # converts point to public key
        if self == INFINITY:
            return '0'

        x = self.affineX()
        y = self.affineY()

        front = 0x02 if y % 2 == 0 else 0x03

        int_key = self.append_hex(front, x)
        unencoded_pubkey = self.add_checksum(int_key)
        leading = "00" if len(unencoded_pubkey[2:]) % 2 == 0 else "0"
        return b58encode(binascii.unhexlify(leading + unencoded_pubkey[2:]))

    @staticmethod
    def add_checksum(int_key):
        # adds checksum to the pubkey
        length = len(hex(int_key)) // 2
        byte_key = int_key.to_bytes(length=length, byteorder="big")
        checksum_hash = rmd160(byte_key)
        checksum = checksum_hash[:8]
        return hex(int_key) + checksum

    @staticmethod
    def append_hex(a, b):
        # appends hex characters a in front of b
        sizeof_b = 0

        # get size of b in bits
        while ((b >> sizeof_b) > 0):
            sizeof_b += 1

        # align answer to nearest 4 bits (hex digit)
        sizeof_b += sizeof_b % 4

        return (a << sizeof_b) | b

    def x(self):
        return self.__x

    def y(self):
        return self.__y

    def z(self):
        return self.__z

    def curve(self):
        return self.__curve

    def order(self):
        return self.__order


# This one point is the Point At Infinity for all purposes:
INFINITY = EOSPoint(None, None, None, None)
