from enum import Enum

class UserRole(Enum):
    OWNER = "creator"
    ADMIN = "administrator"
    MEMBER = "member"

    @classmethod
    def get_roles(self):
        return [role.value for role in UserRole]