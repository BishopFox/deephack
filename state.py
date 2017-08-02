
"""The state of a given episode is what DeepHack has learned about the database."""
class State():
    def __init__(self):
        self.statetable = [""]
        self.current = 0

    def __str__(self):
        out = ""
        for entry in self.statetable:
            out += entry + "\n"
        return out

    def __iter__(self):
        self.current = 0
        return self

    def __next__(self):
        try:
            result = self.statetable[self.current]
            self.current += 1
        except IndexError:
            raise StopIteration
        return result

    def update(self, query):
        query = query.split("%")[0]
        for i, entry in enumerate(self.statetable):
            if query.startswith(entry):
                self.statetable[i] = query
                return
            if entry.startswith(query):
                return
        self.statetable.append(query)

    """Counts up the total length of the state table and calls that the state's value"""
    def value(self):
        value = 0
        for entry in self.statetable:
            value += len(entry)
        return value
