from PIL import Image

def validate():
    """Just validate one transfer"""
    user_input = input("Is this a valid signature? (Y/n): ")
    if user_input.lower() == "y":
        print("It's valid!")
    else:
        print("It's not valid!")

def display_and_verify(filename):
    img = Image.open(filename)
    img.show()
    validate()

if __name__ == "__main__":
    display_and_verify("alice.png")
