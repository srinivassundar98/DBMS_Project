def check_user(username, password):
    # A simple database of users
    users = {
        "srinivas": "password123",
        "user2": "password2"
    }
    return username in users and users[username] == password