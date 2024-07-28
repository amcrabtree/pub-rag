"""
    This script converts a user's directory of PDFs into a vector database.

    USAGE:
        $ python make_vector_db.py [CORPUS TXT DIR] [DATABASE]
"""
import sys
sys.tracebacklimit = 0
import os
from utils import make_database


def validate_user_input(user_input) -> None:
    pub_dir, db_path = user_input
    if (pub_dir == "") or (db_path == ""):
        raise ValueError("Script needs 2 arguments to run.\n")
    if len([f for f in os.listdir(pub_dir) if f.endswith(".pdf")]) == 0:
        raise ValueError("No PDFs found in directory.\n")
    return None


if __name__=="__main__":

    # Sys variables
    pub_dir = sys.argv[1]
    db_path = sys.argv[2]
    validate_user_input([pub_dir, db_path])

    pub_path_list = [os.path.join(pub_dir, f) for f in os.listdir(pub_dir) if f.endswith(".pdf")]
    make_database(db_path, pub_path_list)
    print(f"\nDone! Database saved to {db_path}\n")
