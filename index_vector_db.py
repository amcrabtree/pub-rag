"""
    Creates FAISS index file to expediate similarity searches from the vector db. 

    USAGE:
        $ python index_vector_db.py [DATABASE] [INDEX FILE]
"""
import sys
from utils import make_index_file


def validate_user_input(user_input) -> None:
    db_path, index_path = user_input
    if not db_path.endswith(".db"):
        raise ValueError("Database needs to end in '.db'\n")
    if not index_path.endswith(".index"):
        raise ValueError("Database needs to end in '.index'\n")
    return None
    

if __name__=="__main__":

    db_path = sys.argv[1]
    index_path = sys.argv[2]
    validate_user_input([db_path, index_path])

    make_index_file(db_path, index_path)
    print(f"\nDone! Database saved to {index_path}\n")