from src import create_app

if __name__ == "__main__":
    # TODO: investigage host 0.0.0.0 vs default 127.0.0.1
    create_app("src.conf.DevelopmentConfig").run(host="0.0.0.0")
