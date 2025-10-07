import uuid



class RBUser:
    def __init__(self, user_id: uuid.UUID | None = None,
                 username: str | None = None,
                 email: str | None = None,
                 phone_number: str | None = None,
                 profile: dict | None = None):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.phone_number = phone_number
        self.profile = profile

    def to_dict(self) -> dict:
        return {key: value for key, value in {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'phone_number': self.phone_number,
            'profile': self.profile
        }.items() if value is not None
        }