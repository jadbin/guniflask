from flask import request


class WebAuthenticationDetails:
    def __init__(self):
        self.remote_address = request.remote_addr
