from visualization import create_dashboard

if __name__ == '__main__':
    app = create_dashboard()
    app.run(host='0.0.0.0',debug=False, port=8050)
