from PIL import Image


class PNGCoin:

    def __init__(self, transfers):
        self.transfers = transfers  # Instances of PIL.Image
        self._valid = None

    @staticmethod
    def validate_txn(img):
        img.show()

        user_input = input("Is this a valid signature? (Y/n): ")
        if user_input.lower() == "y":
            return True
        else:
            return False

    def validate_coin(self):
        for txfr in self.transfers:
            if not self.validate_txn(txfr):
                return False

        return True

    @property
    def valid(self):
        if self._valid is None:
            self._valid = self.validate_coin()

        return self._valid


if __name__ == "__main__":
    coin = PNGCoin([
        Image.open("alice.png"),
        Image.open("alice-to-bob.png"),
    ])

    bad_coin = PNGCoin([
        Image.open("alice.png"),
        Image.open("alice-to-bob-forged.png"),
    ])

    print(coin.valid)
    print(bad_coin.valid)
