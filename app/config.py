import os

class Settings:
    # Set active profession (Can be switched dynamically later)
    ACTIVE_PROFESSION: str = os.getenv("ACTIVE_PROFESSION", "Plumbing")
    
    # SQLite Database URI
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./global_skilled.db")
    
    # Your target trades CV profile for matching logic
    USER_CV: str = """
    Certified Plumber with over 20 years of career experience in plumbing. 
    Holds an educational certificate as a general fitter in mechanical engineering.
    Specializes in commercial and industrial piping installations, construction, 
    and supervisory duties.
    """

settings = Settings()
