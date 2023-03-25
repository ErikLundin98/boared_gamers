from app.server import app

def main():
    app.run(debug=False, host="0.0.0.0")

if __name__ == "__main__":
    main()