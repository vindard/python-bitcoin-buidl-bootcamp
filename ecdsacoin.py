from pathlib import Path
import pickle

from ecdsa import SigningKey, SECP256k1, BadSignatureError

BANK = Bank()


class Transaction:

    def __init__(self, signature, public_key):
        self.signature = signature
        self.public_key = public_key
        self.msg = pickle.dumps(public_key)

        self.valid = None
        self.validate_txn()

    def validate_txn(self):
        try:
            self.valid = BANK.public_key.verify(self.signature, self.msg)
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


class Bank:

    def __init__(self):
        self.private_key = SigningKey.generate(curve=SECP256k1)
        self.public_key = self.private_key.get_verifying_key()

    def issue(self, public_key):
        msg = pickle.dumps(public_key)

        signature = self.private_key.sign(msg)
        txn = Transaction(signature, public_key)

        coin = ECDSACoin([txn])

        return coin


if __name__ == "__main__":
    # Create good coin
    print("Creating 'coin'...")
    coin = ECDSACoin([])
    print("'coin' valid?:", coin.valid, '\n')

    # Create bad coin
    print("Creating 'bad_coin'...")
    bad_coin = ECDSACoin([])
    print("'bad_coin' valid?:", bad_coin.valid, '\n')

    # Save good coin to disk and load back into memory
    filename = 'bob.pngcoin'
    coin.to_disk(filename)
    bobs_coin = ECDSACoin.load_from_disk(filename)
    print("Verify loaded coin:", bobs_coin.transactions == coin.transactions)
