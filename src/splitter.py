import re

class ManPageSplitter:
    def __init__(self, man_page_path: str):
        self.man_page_path = man_page_path

if __name__ == "__main__":
    print("Splitting man page...")
    splitter = ManPageSplitter("data/cat.txt")