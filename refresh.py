import db_access
import datetime

def main():
    db_access.refresh_match(datetime.datetime.now())


if __name__ == '__main__':
    main()