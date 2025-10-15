from sqlmodel import SQLModel,create_engine,Session

# -------------------------------
# DATABASE SETUP
# -------------------------------

# Define SQLite database file name and connection URL
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# `check_same_thread=False` is required for SQLite to allow multiple threads (used by FastAPI)-to handle multiple requests
connect_args = {"check_same_thread": False}

# Create a database engine (used for all connections)
engine = create_engine(sqlite_url, connect_args=connect_args)

# -------------------------------
# CREATE DATABASE TABLES
# -------------------------------
def create_db_and_tables():
    """Verify if the provided plain password matches the stored hash."""
    SQLModel.metadata.create_all(engine)

# -------------------------------
# SESSION GENERATOR
# -------------------------------
def get_session():
    """Dependency that provides a database session for each request."""
    with Session(engine) as session:
        yield session

