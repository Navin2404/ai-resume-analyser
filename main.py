# main.py — One file-la everything control pannuvom

import sys
# sys.argv — command line arguments read pannuvom
# python main.py document.pdf
# sys.argv = ["main.py", "document.pdf"]

from ingest import ingest
from chatbot import chat

# Other files-la irukka functions import pannuvom

if __name__ == "__main__":

    if len(sys.argv) > 1:
        # Command line-la file name kudutanga?
        # python main.py myfile.pdf — ila

        pdf_file = sys.argv[1]
        # sys.argv[1] — second argument = pdf filename

        print(f"Ingesting {pdf_file}...")
        ingest(pdf_file)
        print("\nNow starting chat...\n")

    chat()
    # Always chat mode start aagum