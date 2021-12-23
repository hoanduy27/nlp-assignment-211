from abc import ABC, abstractmethod
from functools import reduce
from .lexicon import city_abbrv


TO_PATT = {
    'AGENT': 'LSUBJ',
    'FROM-LOC': 'FROM-LOC',
    'TO-LOC': 'TO-LOC',
    'DEPART-AT': 'DEPART-AT',
    'ARRIVE-AT': 'ARRIVE-AT',
    'RUN-IN': 'RUN-IN',
}


class Variable(ABC):
    pass

class PRED(Variable):
    def __init__(self, name, val):
        self.name = name
        self.val = val
    
    def __str__(self):
        return f'"{self.val}" {self.name}'

    def __repr__(self) -> str:
        return self.__str__()

    def patt(self):
        return f'{self.name} PRED {self.val}'

class Exp(Variable):
    def __init__(self, typ, pred, val):
        self.typ = typ #AGENT, FROM-LOC, TO-LOC, DEPART-AT, ARRIVE-AT, RUN-IN
        self.pred = pred
        self.val = val # Literal or Wh-Query

    def __str__(self):
        val = f'({str(self.val)})' if isinstance(self.val, Literal) else str(self.val.name)
        return f'{self.typ} {self.pred.name} {str(val)}'

    def patt(self):
        val = f'({str(self.val)})' if isinstance(self.val, Literal) else str(self.val.name)
        return f'{self.pred.name} {TO_PATT[self.typ]} {str(val)}'
    
    def __repr__(self) -> str:
        return self.__str__()

class Literal(Variable):
    def __init__(self, typ, name, val):
        self.typ = typ #TRAIN-NAME, CITY-NAME, TIMEMOD
        self.name = name
        self.val = val
    
    def __str__(self):
        return f'{self.typ} {self.name} "{self.val}"'

    def __repr__(self) -> str:
        return self.__str__()

class Query(Variable):
    pass

class Wh_Query(Query):
    def __init__(self, typ, name):
        self.typ = typ # Train, ATime, DTime, Runtime
        self.name = name
    
    def __str__(self):
        return f'Wh-{self.typ} {self.name}'

    def __repr__(self) -> str:
        return self.__str__()

    def patt(self):
        return self.__str__()

class YN(Query):
    def __str__(self):
        return 'YN'

    def __repr__(self) -> str:
        return self.__str__()

    def patt(self):
        return self.__str__()

class Context:
    def __init__(self, pred, from_loc, to_loc, procedure_var):
        self.pred = pred
        self.from_loc = from_loc
        self.to_loc = to_loc
        self.procedure_var = procedure_var

class GrammaticalRelation:
    def __init__(self, relation_set):
        # Dependency parsing result
        self.relation_set = relation_set 
        self.pattern_set = []
        self.query_set = []
        self.context = Context(
            None, False, False,
            {
                'TRAIN': '?t',
                'D-CITY': '?dc',
                'A-CITY': '?ac',
                'DTIME': '?dt',
                'ATIME': '?at',
                'RUN-TIME': '?rt',

            }
        )

    def add_pred(self):
        sub_rel = filter(lambda rel: rel.rule.name == 'ROOT', self.relation_set)
        for rel in sub_rel:
            self.pattern_set.append(
                PRED('v1', rel.dep_token.word.upper())
            )
            self.context.pred = self.pattern_set[-1]

    def add_depart_city(self):
        sub_rel = filter(lambda rel: rel.rule.name == 'case-d', self.relation_set)
        for rel in sub_rel:
            city = rel.dom_token.word.upper()
            self.context.procedure_var['D-CITY'] = city_abbrv[city]
            self.pattern_set.append(
                Exp(
                    'FROM-LOC', 
                    self.context.pred, 
                    Literal('CITY-NAME', 'c1', city)
                )
            )
            self.context.from_loc = True
    def add_arrive_city(self):
        sub_rel = filter(lambda rel: rel.rule.name in ['case-a', 'dobj-a'], self.relation_set)
        for rel in sub_rel:
            tok = rel.dom_token if rel.rule.name == 'case-a' else rel.dep_token
            city = tok.word.upper()
            self.context.procedure_var['A-CITY'] = city_abbrv[city]
            self.pattern_set.append(
                Exp(
                    'TO-LOC',
                    self.context.pred,
                    Literal('CITY-NAME', 'c2', city)
                )
            )
            self.context.to_loc = True

    def add_timemod(self):
        sub_rel = filter(lambda rel: rel.rule.name in ['case-t', 'case-t-wh', 'is'], self.relation_set)


        if self.context.from_loc and self.context.to_loc:
            qtyp = 'Runtime'
            typ = 'RUN-IN'
            var = 'RUN-TIME'
            name = 'r1'
        elif self.context.from_loc:
            qtyp = 'DTime'
            typ = 'DEPART-AT'
            var = 'DTIME'
            name = 'd1'
        else:
            qtyp = 'ATime'
            typ = 'ARRIVE-AT'
            var = 'ATIME'
            name = 'a1'

        for rel in sub_rel:
            # Normal type
            if(rel.rule.name in ['case-t']):
                tok = rel.dom_token
                timemod = tok.word.upper()
                self.context.procedure_var[var] = timemod

                self.pattern_set.append(
                    Exp(
                        typ,
                        self.context.pred,
                        Literal('TIMEMOD', name, timemod)
                    )
                )
            # Query type
            else:
                query = Wh_Query(qtyp, name)
                self.query_set.append(query)
                self.pattern_set.append(
                    Exp(
                        typ,
                        self.context.pred,
                        query
                    )
                )


    def add_agent(self):
        sub_rel = filter(lambda rel: rel.rule.name in ['namemod', 'det-wh'], self.relation_set)
        for rel in sub_rel:
            # Normal type
            if rel.rule.name == 'namemod':
                train_name = rel.dep_token.word.upper()
                self.context.procedure_var['TRAIN'] = train_name
                self.pattern_set.append(
                    Exp(
                        'AGENT',
                        self.context.pred,
                        Literal('TRAIN-NAME', 't1', train_name)
                    )
                )
            # Query type
            else:
                query = Wh_Query('Train', 't1')
                self.query_set.append(query)
                self.pattern_set.append(
                    Exp(
                        'AGENT',
                        self.context.pred,
                        query
                    )
                )

    def add_yesno(self):
        sub_rel = list(filter(lambda rel: rel.rule.name == 'advmod', self.relation_set))
        if len(sub_rel) > 0:
            self.query_set.append(YN())

    def generate(self):
        self.add_pred()
        self.add_agent()
        self.add_depart_city()
        self.add_arrive_city()
        self.add_timemod()
        self.add_yesno()
        
    def get_grammatical_relation(self):
        return '\n'.join([f'({x.patt()})' for x in self.query_set + self.pattern_set])

    def get_logical_form(self):
        queries = ' '.join([str(x) for x in self.query_set])
        attrib = ' '.join([f'({str(pattern)})' for pattern in self.pattern_set])
        return f'({queries}: {attrib})'

