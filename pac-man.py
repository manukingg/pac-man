import sys
from src.parser import Parser

if __name__ == "__main__":
    if len(sys.argv) == 2:
        try:
            parser = Parser(sys.argv[1])
            config = parser.parse()
            print(config.levels)
        except Exception as e:
            print(e)
    else:
        print("Invalid run format")