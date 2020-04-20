from pathlib import Path
import pickle

from PIL import Image


class PNGCoin:

    def __init__(self, transfers):
        self.transfers = transfers  # Instances of PIL.Image
        self.valid = None
        self.validate_coin()

    @staticmethod
    def validate_txn(img):
        img.show()

        user_input = input("Is this a valid signature? (Y/n): ")
        if user_input.lower() == "y":
            return True
        else:
            return False

    def validate_coin(self):
        self.valid = True
        for txfr in self.transfers:
            if not self.validate_txn(txfr):
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
    images = Path("pngcoin_images")

    # Create good coin
    print("Creating 'coin'...")
    coin = PNGCoin([
        Image.open(images/"alice.png"),
        Image.open(images/"alice-to-bob.png"),
    ])
    print("'coin' valid?:", coin.valid, '\n')

    # Create bad coin
    print("Creating 'bad_coin'...")
    bad_coin = PNGCoin([
        Image.open(images/"alice.png"),
        Image.open(images/"alice-to-bob-forged.png"),
    ])
    print("'bad_coin' valid?:", bad_coin.valid, '\n')

    # Save good coin to disk and load back into memory
    filename = 'bob.pngcoin'
    coin.to_disk(filename)
    bobs_coin = PNGCoin.load_from_disk(filename)
    print("Verify loaded coin:", bobs_coin.transfers == coin.transfers)
