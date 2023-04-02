from app.server import app
import argparse

parser = argparse.ArgumentParser(
    prog="boared_app",
    description="A simple board game tournament tracking application",
)

parser.add_argument('-p', '--port', default=5000)
parser.add_argument('--host', default="0.0.0.0")
parser.add_argument('-d', '--debug', default=False)

def main():
    args = parser.parse_args()
    app.run(debug=args.debug, host=args.host, port=args.port)

if __name__ == "__main__":
    main()