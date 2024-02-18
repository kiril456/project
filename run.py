from web_app import app, db


if __name__ == "__main__":
    with app.app_context():         # <--- without these two lines, 
        db.create_all()             # <--- we get the OperationalError in the title
        app.run(debug=True)
    