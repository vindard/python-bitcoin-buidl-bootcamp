import json
from pathlib import Path
import pickle

from ecdsa import SigningKey, VerifyingKey, SECP256k1, BadSignatureError


def encode_msg(prev_txn, wallet):
    '''
    Creates a message and encodes it to bytes
    format so that it can be passed to ecdsa
    'sign' function.
    '''
    prev_sig = None
    if prev_txn:
        prev_sig = prev_txn.signature.hex()

    msg = {
    'previous_signature': prev_sig,
    'payee_public_key': wallet.public_key.to_pem().decode()
    }
    msg_bytes = json.dumps(msg).encode()

    return msg_bytes

def decode_msg(msg_bytes):
    msg_json = msg_bytes.decode()
    msg = json.loads(msg_json)

    prev_sig = None
    prev_sig_hex = msg['previous_signature']
    if prev_sig_hex:
        prev_sig = bytes.fromhex(prev_sig_hex)

    pub_key_str = msg['payee_public_key']
    k = pub_key_str.encode()

    return prev_sig, pub_key(k)

def pub_key(public_key_bytes):
    return VerifyingKey.from_pem(public_key_bytes)

def priv_key(private_key_bytes):
    return SigningKey.from_pem(private_key_bytes)

def make_txn(coin, wallet, prev_owner):
    prev_txn = coin.last_txn if coin else None
    msg_bytes = encode_msg(prev_txn, wallet)
    signature = prev_owner.private_key.sign(msg_bytes)

    return Transaction(signature, wallet, prev_txn, prev_owner)

def verify_sig(signature, msg_bytes, verifying_key_bytes):
    try:
        public_key = pub_key(verifying_key_bytes)
        valid = public_key.verify(signature, msg_bytes)
    except BadSignatureError:
        valid = False

    return valid

class Wallet:

    def __init__(self, owner_name="Anon"):
        self.private_key = SigningKey.generate(curve=SECP256k1)
        self.public_key = self.private_key.get_verifying_key()
        self.owner_name = owner_name
        self.coins = []

    def receive(self, coin):
        if coin.valid:
            self.coins.append(coin)
        else:
            print("Invalid coin passed, discarding...")

    def send(self, wallet):
        if not self.coins:
            print("No coins to spend")
            return

        coin = self.coins[-1]
        txn = make_txn(coin, wallet, prev_owner=self)

        ok, _ = coin.transfer(txn)
        if ok:
            print(f"Sending coin from '{self.owner_name}'' to '{wallet.owner_name}''")
            wallet.receive(coin)
            self.coins.pop()

        return coin


class Bank(Wallet):

    def __init__(self, owner_name=None):
        owner_name = owner_name or "Official Bank"
        super().__init__(owner_name)

    def issue(self, wallet):
        txn = make_txn(coin=None, wallet=wallet, prev_owner=self)
        coin = ECDSACoin([txn])
        wallet.receive(coin)

        return coin


BANK = Bank()

class Transaction:

    def __init__(self, tx_signature, owner, prev_txn, prev_owner):
        self.signature = tx_signature
        self.prev_txn = prev_txn
        self.msg_bytes = encode_msg(prev_txn, owner)

        # Unpack to bytes to allow pickling of 'Transaction' class
        self.owner_pub_key_bytes = owner.public_key.to_pem()
        self.prev_pub_key_bytes = prev_owner.public_key.to_pem()

        self._valid = None


    def __eq__(self, other):
        sigs_equal = (self.signature == other.signature)
        keys_equal = (self.msg_bytes == other.msg_bytes)

        return sigs_equal and keys_equal

    @property
    def valid(self):
        self.validate_txn()

        return self._valid

    def validate_txn(self):
        self._valid = \
            (self.prev_txn is not None or
                pub_key(self.prev_pub_key_bytes) == BANK.public_key) \
            and \
            verify_sig(self.signature, self.msg_bytes, self.prev_pub_key_bytes)


class ECDSACoin:

    '''
    Note: 'to_pem' is used for any private/public keys stored
    with this class because the non-pem objects can't be pickled
    to be stored on disk.

    The keys can be retrieved by simply calling the 'from_pem'
    method on the SigningKey/Verifying objects and passing in the
    pem bytes version of they key to it.
    '''

    def __init__(self, transactions):
        self.transactions = transactions
        self._valid = None


    @property
    def valid(self):
        self.validate_coin()

        return self._valid

    def validate_coin(self):
        self._valid = True
        for txn in self.transactions:
            if not txn.valid:
                self._valid = False
                break

    @property
    def owner(self):
        latest_txn = self.transactions[-1]
        k = latest_txn.owner_pub_key_bytes

        print(f"Coin has {len(self.transactions)} transaction(s)")
        return pub_key(k)

    def owner_name(self, entities=None):
        if entities is None:
            entities = {}

        return entities.get(self.owner.to_pem())

    @property
    def serialized(self):
        return pickle.dumps(self)

    def to_disk(self, filename):
        with open(filename, "wb") as f:
            f.write(self.serialized)

    @property
    def last_txn(self):
        return self.transactions[-1]

    @staticmethod
    def load(coin_bytes):
        return pickle.loads(coin_bytes)

    @classmethod
    def load_from_disk(cls, filename):
        with open(filename, 'rb') as f:
            coin_bytes = f.read()

        return cls.load(coin_bytes)


    def transfer(self, txn):
        ok, error_msg = True, ''

        if txn.valid:
            prev_sig, _ = decode_msg(txn.msg_bytes)
            prev_txn = self.transactions[-1]
            if prev_sig == prev_txn.signature:
                self.transactions.append(txn)
            else:
                ok = False
                error_msg = "Previous signatures don't match"
        else:
            ok = False
            error_msg = "Transaction has bad signature"

        if error_msg:
            print(error_msg)

        return ok, error_msg


if __name__ == "__main__":
    alice = Wallet('Alice')
    bob = Wallet('Bob')

    # Create good coin
    print("Creating 'coin'...")
    coin = BANK.issue(alice)
    print("'coin' valid?:", coin.valid, '\n')

    # Create bad coin
    print("Creating 'bad_coin'...")
    fake_bank = Bank('Fake Bank')
    bad_coin = fake_bank.issue(alice)
    print("'bad_coin' valid?:", bad_coin.valid, '\n')

    entities = {
        alice.public_key.to_pem(): "Alice",
        bob.public_key.to_pem(): "Bob",
        fake_bank.public_key.to_pem(): "Fake Bank",
        BANK.public_key.to_pem(): "Bank",
    }

    # Save good coin to disk and load back into memory
    filename = 'alice.pngcoin'
    coin.to_disk(filename)
    alice_coin = ECDSACoin.load_from_disk(filename)
    print("Verify loaded coin:", alice_coin.transactions == coin.transactions)
