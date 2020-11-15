class Error:
    
    def __init__(self, type, title, status, detail):
        self.type = type
        self.title = title
        self.status = status
        self.detail = detail

    def get(self):
        return {
            "type":self.type,
            "title":self.title,
            "status":self.status,
            "detail":self.detail,
        },self.status

class Error400(Error):
    
    def __init__(self, type, detail):
        self.type = "badrequest:"+type
        self.title = "Bad Request"
        self.status = 400
        self.detail = detail

class Error404(Error):
    
    def __init__(self, type, detail):
        self.type = "notfound:"+type
        self.title = "Not Found"
        self.status = 404
        self.detail = detail

class Error500(Error):
    
    def __init__(self):
        self.type = "tryagain"
        self.title = "Try Again"
        self.status = 500
        self.detail = "An error occured, please try again"