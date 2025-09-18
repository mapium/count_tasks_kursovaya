# class Users():
#     def __init(self, id, username, password_hash, employee_id, create_at, last_login):
#         self.id=id
#         self.username=username
#         self.password_hash=password_hash
#         self.employee_id=employee_id
#         self.create_at=create_at
#         self.last_login=last_login

#     def __repr__(self):
#         return(Users({self.id}, {self.username}, {self.password_hash}, {self.employee_id}, {self.create_at}, {self.last_login}))
class Users():
    def __init(self, id, username, password_hashed):
        self.id=id
        self.username=username
        self.password_hashed=password_hashed

    def __repr__(self):
        return(Users({self.id}, {self.username}, {self.password_hashed} ))