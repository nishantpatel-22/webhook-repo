from app import create_app

app = create_app()

if __name__ == '__main__':
    print("Starting the TechStaX Webhook Receiver on port 5000...")
    # host='0.0.0.0' makes it accessible through ngrok
    app.run(host='0.0.0.0', port=5000, debug=True)