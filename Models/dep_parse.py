from .tokenization import Token
class Rule:
    def __init__(self, name, typ):
        self.typ = typ #Left, Right, Shift, Reduce
        self.name = name 

    def __str__(self):
        return self.name

class Relation:
    def __init__(self, rule, dom_token, dep_token):
        self.rule = rule
        self.dom_token = dom_token
        self.dep_token = dep_token
    def __str__(self) -> str:
        return f'{self.rule.name}({self.dom_token.word}, {self.dep_token.word})'

    def __repr__(self) -> str:
        return self.__str__()
        
class DependencyParsing:
    def __init__(self, leftarcs, rightarcs, token_list, verbose=0):
        self.ROOT = 'ROOT'
        # self.ruleset = ruleset
        self.ruleset = {'L': leftarcs, 'R': rightarcs}
        # list[Token]
        self.stack = [Token(self.ROOT, self.ROOT)]
        # list[Token]
        self.buffer = token_list
        self.relation_set = []
        self.verbose = verbose

    def __str__(self) -> str:
        return f'Stack: {self.stack}\nBuffer: {self.buffer}\nRelation: {self.relation_set}\n'

    def leftarc(self, rule):
        assert rule.typ == 'Left'
        assert len(self.stack) > 1
        assert len(self.buffer) >= 0
        self.relation_set.append(Relation(rule, self.buffer[0], self.stack[-1]))
        self.stack.pop()
        if self.verbose==1:
            print(f'LeftArc: {rule}\n---')
            print(str(self))

    def _shift(self):
        assert len(self.stack) >= 1
        assert len(self.buffer) > 0
        self.stack.append(self.buffer[0])
        self.buffer.pop(0)

    def rightarc(self, rule):
        self._shift()
        self.relation_set.append(Relation(rule, self.stack[-2], self.stack[-1]))
        if self.verbose==1:
            print(f'RightArc: {rule}\n---')
            print(str(self))

    def shift(self):
        self._shift()
        if self.verbose==1:
            print(f'Shift\n---')
            print(str(self))

    def rduce(self):
        assert len(self.stack) > 1
        self.stack.pop()
        if self.verbose==1:
            print(f'Reduce\n---')
            print(str(self))

    def current_pair(self):
        return self.stack[-1].pos, self.buffer[0].pos

    def parse(self):
        self.shift()
        while len(self.buffer) > 0:
            if self.current_pair() in self.ruleset['L']:
                rule = self.ruleset['L'][self.current_pair()]
                self.leftarc(rule)
            elif self.current_pair() in self.ruleset['R']:
                rule = self.ruleset['R'][self.current_pair()]
                self.rightarc(rule)
                if self.stack[-1].pos not in ['ARRIVE-V', 'TRAIN-V']:
                    self.rduce()
            else:
                self.shift()
        return self.relation_set