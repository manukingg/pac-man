from src.models import Config
from src.app import Application

if __name__ == "__main__":
    config = Config()
    app = Application(config)
    app.run()