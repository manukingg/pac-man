import sys
from src.app import Application
from src.parser import Parser

if __name__ == "__main__":
    if len(sys.argv) == 2:
        try:
            parser = Parser(sys.argv[1])
            config = parser.parse()
            app = Application(config)
            app.run()
        except Exception as e:
            print(e)
    else:
        print("Invalid run format")
