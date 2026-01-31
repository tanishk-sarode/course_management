import enum

class RoleEnum(str, enum.Enum):
    student = "student"
    instructor = "instructor"
    # admin = "admin"

class CourseCategory(str, enum.Enum):
    programming = "programming"
    design = "design"
    marketing = "marketing"
    business = "business"

class CourseLevel(str, enum.Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"

class EnrollmentStatus(str, enum.Enum):
    active = "active"
    dropped = "dropped"
    completed = "completed"