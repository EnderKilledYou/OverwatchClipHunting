class RegionResult:
    def __init__(self, did_pass: bool, text: str, matched: str):
        self.did_pass = did_pass
        self.text = text
        self.matched = matched
