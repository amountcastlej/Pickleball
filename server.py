from pickleball_app import app
from pickleball_app.controllers import user_controllers, event_controllers

if __name__=="__main__":
    app.run(debug=True)