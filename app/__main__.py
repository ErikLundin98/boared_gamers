from app.server import app

def main():
    app.run(debug=False, host="0.0.0.0", port=3000)

if __name__ == "__main__":
    main()