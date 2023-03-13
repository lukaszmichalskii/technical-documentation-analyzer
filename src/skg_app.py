import sys

if __name__ == "__main__":
    if sys.version_info[:2] < (3, 8):
        sys.exit(
            "Python {}.{}.{} is not supported. You should run app with Python 3.8 or later".format(
                *sys.version_info[:3]
            )
        )
    import src.application.main

    sys.exit(src.application.main.main(sys.argv))
