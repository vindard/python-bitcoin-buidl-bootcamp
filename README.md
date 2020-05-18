## BUIDL Bootcamp Step Through

This repo will be an exercise space as I step through [Justin Moon's BUIDL Bootcamp](https://mooniversity.io/courses/digital-cash) again. The course is one in understanding some of the underlying concepts behind Bitcoin. It achieves this by starting with a very naive implementation of digital cash and then progressively builds up to Bitcoin by solving problems with our system along the way.

The different steps in getting to Bitcoin will be:
1. [**PNGCoin**](https://github.com/vindard/python-bitcoin-buidl-bootcamp/pull/1)

    PNGCoin is implemented as a naive scheme that uses pictures with handwritten signatures on them to model a digital cash system. It introduces the concept of a 'coin' as a chain of transactions from issuance to current owner by a series of 'transfer' images to represent the transactions.

    Run with: `$ python3 pngcoin.py`

1. [**ECDSACoin**](https://github.com/vindard/python-bitcoin-buidl-bootcamp/pull/2)

    ECDSACoin improves on PNGCoin by swapping out physical signatures for digital cryptographically-robust `ecdsa` signatures. These digital signatures are a significant improvement in terms of being robust against fakes and forgery. A transfer is now a cryptographiccally signed message about the sender and recipient instead of a png image of simple handwritten statement of same.

    A 'coin' is also still a chain of transactions in this implementation, but instead of merely being a loosely coupled list of images we now include information about the previous transaction and hash this information into the transaction to cryptographically chain transactions together. This again gives us a much more robust and forgery-resistant chain of transactions to represent how the coin has moved since its minting.

    Run with: `$ python3 ecdsacoin.py`

1. ***BankCoin***

    *To be implemented...*

1. ***DivisiCoin***

    *To be implemented...*

1. ***BlockCoin***

    *To be implemented...*

1. ***HashCoin***

    *To be implemented...*

1. **Bitcoin**

    *To be implemented...*

---

### As a learning resouce

Each implementation will be built up in separate branches and then PR'd into the `develop` branch. Commits will be written to progressively build up the implementation and describe the process.

To follow along with any implementation, simply go to that implementation's PR and step through the commits to see how that implementation was built up.
