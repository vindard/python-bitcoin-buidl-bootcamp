import json
from pathlib import Path
import pickle

from ecdsa import SigningKey, VerifyingKey, SECP256k1, BadSignatureError


def encode_msg(prev_txn, wallet):
    prev_sig = None
    if prev_txn:
        prev_sig = prev_txn.signature.hex()

    msg = {
    'previous_signature': prev_sig,
    'payee_public_key': wallet.public_key.to_pem().decode()
    }
    msg_bytes = json.dumps(msg).encode()

    return msg_bytes


class Wallet:

    def __init__(self, owner="Anon"):
        self.private_key = SigningKey.generate(curve=SECP256k1)
        self.public_key = self.private_key.get_verifying_key()
        self.coins = []

    def receive(self, coin):
        if coin.valid:
            self.coins.append(coin)
        else:
            print("Invalid coin passed, discarding...")


class Bank(Wallet):

    def __init__(self):
        super().__init__(owner='Bank')

    def issue(self, wallet):
        msg_bytes = encode_msg(None, wallet)
        signature = self.private_key.sign(msg_bytes)
        txn = Transaction(signature, msg_bytes)

        coin = ECDSACoin([txn])
        wallet.receive(coin)

        return coin


BANK = Bank()

class Transaction:


    def __init__(self, signature, msg, owner=None):
        self.signature = signature
        self.msg = msg
        self.owner_public_key_bytes = \
            owner.public_key.to_pem() if owner else \
            BANK.public_key.to_pem()

        self.valid = None
        self.validate_txn()

    def __eq__(self, other):
        sigs_equal = (self.signature == other.signature)
        keys_equal = (self.msg == other.msg)

        return sigs_equal and keys_equal

    def validate_txn(self):
        try:
            pub_key = VerifyingKey.from_pem(self.owner_public_key_bytes)
            self.valid = pub_key.verify(self.signature, self.msg)
        except BadSignatureError:
            self.valid = False


class ECDSACoin:

    def __init__(self, transactions):
        self.transactions = transactions
        self.valid = None
        self.validate_coin()

    def validate_coin(self):
        self.valid = True
        for txn in self.transactions:
            if not txn.valid:
                self.valid = False
                break

    @property
    def serialized(self):
        return pickle.dumps(self)

    def to_disk(self, filename):
        with open(filename, "wb") as f:
            f.write(self.serialized)

    @staticmethod
    def load(coin_bytes):
        return pickle.loads(coin_bytes)

    @classmethod
    def load_from_disk(cls, filename):
        with open(filename, 'rb') as f:
            coin_bytes = f.read()
            return cls.load(coin_bytes)


if __name__ == "__main__":
    alice = Wallet('Alice')
    bob = Wallet('Bob')

    # Create good coin
    print("Creating 'coin'...")
    coin = BANK.issue(alice)
    print("'coin' valid?:", coin.valid, '\n')

    # Create bad coin
    print("Creating 'bad_coin'...")
    fake_bank = Bank()
    bad_coin = fake_bank.issue(alice)
    print("'bad_coin' valid?:", bad_coin.valid, '\n')

    # Save good coin to disk and load back into memory
    filename = 'alice.pngcoin'
    coin.to_disk(filename)
    alice_coin = ECDSACoin.load_from_disk(filename)
    print("Verify loaded coin:", alice_coin.transactions == coin.transactions)
