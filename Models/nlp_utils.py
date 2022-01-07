from nltk import parse

class Token:
    def __init__(self, word, pos):
        self.word = word 
        self.pos = pos 
    
    def __str__(self):
        return f'{self.word} ({self.pos})'

    def __repr__(self):
        return self.__str__()


def tokenize(grammar, text):
    nlp_grammar = parse.load_parser(grammar, trace = 0)
    tree = nlp_grammar.parse_one(text.split())

    token_list = []
    for s in tree.subtrees(lambda t: t.height() == 2):
        pos = str(s.label())
        word = ' '.join(s.leaves())
        token_list.append(Token(word, pos))
    return token_list

class Database:
    def __init__(self, raw_db_path):
        self.trains = []
        self.atimes = []
        self.dtimes = []
        self.runtimes = []
        # Read each line in raw_db
        with open(raw_db_path, 'r', encoding='utf-8') as f:
            rows = f.readlines()
            for row in rows:
                row = ' '.join(row.strip().replace('(', ' ').replace(')', ' ').split())
                if 'TRAIN' in row:
                    self.trains.append(row)
                elif 'ATIME' in row:
                    self.atimes.append(row)
                elif 'DTIME' in row:
                    self.dtimes.append(row)
                elif 'RUN-TIME' in row:
                    self.runtimes.append(row)
              
    def __str__(self):
        return '\n'.join(self.trains + self.atimes + self.dtimes + self.runtimes)

class Printout:
    def __init__(self, buffer, verbose):
        self.buffer = buffer
        self.verbose = verbose

    def print(self, content):
        if self.verbose:
            self.buffer.append(str(content))

    def __str__(self) -> str:
        return '\n'.join(self.buffer)
