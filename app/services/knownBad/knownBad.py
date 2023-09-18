from app.database import db


def main():
    myDB = db(config_file="server.cfg")
    myDB.cleanKnownBad()
    myDB.buildKnownBad()


if __name__ == "__main__":
    main()
