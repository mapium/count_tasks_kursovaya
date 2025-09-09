class Employees():
    def __init__(self,user_id,first_name,last_name,middle_name,phone_number,email,passport_data,inn,snils,department_id):
        self.user_id=user_id
        self.first_name=first_name
        self.last_name=last_name
        self.middle_name=middle_name
        self.phone_number=phone_number
        self.email=email
        self.passport_data=passport_data
        self.inn=inn
        self.snils=snils
        self.department_id=department_id

    def __repr__(self):
        return(Employees({self.user_id},{self.first_name},{self.last_name},{self.middle_name},{self.phone_number},{self.email},{self.passport_data},{self.inn},{self.snils},{self.department_id}))