import re

class TextParser:
    def _find_match(self, text: str, pattern: str):
        m = re.match(pattern, text)
        if m:
            print("Match found:", m.group())
        else:
            print("No match found")

    def _find_all(self, pattern: str, text: str):
        m = re.findall(pattern, text)
        print(m)

    def _search_string(self, pattern: str, text: str):
        m = re.search(pattern, text)
        if m:
            print(f"Match found: {m.group()}")
        else:
            print("Match not found")

    def _find_iter(self, pattern: str, text: str):
        m = re.finditer(pattern, text)
        for match in m:
            print(f"Match found at {match.start()}")

    def _sub(self, pattern: str, text: str, repl: str):
        new_text = re.sub(pattern, repl, text)
        print(new_text)

    def _validate_email(self, email: str):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        match = bool(re.match(pattern, email))
        print(match)

    def _validate_cell(self, cell: str):
        pattern = r'^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$'
        match = bool(re.match(pattern, cell))
        print(match)

    def _check_password_strength(self, password):
        checks = {
            "length" : len(password) >= 8,
            "uppercase" : bool(re.search("[A-Z]", password)),
            "lowercase" : bool(re.search("[a-z]", password)),
        }
        return print(checks)

def main():

    p = TextParser()
    text = "My phone number is (515) 313-8126, it has an Iowa area code."

    # p._find_match("My", text)
    # p._search_string("Iowa", text)
    # p._find_all("515", text)
    # p._find_iter("5", text)
    # p._sub("phone", text, "cell")

    # big = "100,000,000,000.000,000.000,000"
    # pattern = "[.,]"
    # new_big = re.split(pattern, big)
    # print("\n".join(new_big))

    # p._validate_email("kan%ep@gmail.com")

    # cells = ["(937) 831-6954", "(937) 83r-6954", "(97) 31-6954", "(937) 831-1111"]
    # for cell in cells:    
    #     check = p._validate_cell(cell)
    #     if check == False:
    #         print(f"{cell} is not valid")

    p._check_password_strength("WW3Dh676767")


    
    
if __name__ == "__main__":
    main()