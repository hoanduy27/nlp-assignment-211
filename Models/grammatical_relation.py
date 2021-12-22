from abc import ABC, abstractmethod
from .lexicon import city_abbrv
from functools import reduce
class Variable(ABC):
    pass

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

class Exp(Variable):
    def __init__(self, typ, pred, val):
        self.typ = typ #AGENT, FROM-LOC, TO-LOC, DEPART-AT, ARRIVE-AT, RUN-IN
        self.pred = pred
        self.val = val # Literal or Wh-Query

    def __str__(self):
        val = f'({str(self.val)})' if isinstance(self.val, Literal) else str(self.val.name)
        return f'{self.typ} {self.pred.name} {str(val)}'
    
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

class YN(Query):
    def __str__(self):
        return 'YN'

    def __repr__(self) -> str:
        return self.__str__()

class Procedure:
    def __init__(self, name, var):
        self.name = name
        self.var = var
    
    def __str__(self):
        return f'{self.name} {self.var}' if self.var is not None else self.name

    def __repr__(self) -> str:
        return self.__str__()

class GrammaticalRelation:
    def __init__(self, relation_set):
        # Dependency parsing result
        self.relation_set = relation_set 
        self.pattern_set = []
        self.query_set = []
        self.context = {'pred': None, 'FROM-LOC': False,  'TO-LOC': False}
        self.procedure_var = {
            'TRAIN': '?t',
            'D-CITY': '?dc',
            'A-CITY': '?ac',
            'DTIME': '?dt',
            'ATIME': '?at',
            'RUN-TIME': '?rt',
        }

    def add_pred(self):
        sub_rel = filter(lambda rel: rel.rule.name == 'ROOT', self.relation_set)
        for rel in sub_rel:
            self.pattern_set.append(
                PRED('v1', rel.dep_token.word.upper())
            )
            self.context['pred'] = self.pattern_set[-1]

    def add_depart_city(self):
        sub_rel = filter(lambda rel: rel.rule.name == 'case-d', self.relation_set)
        for rel in sub_rel:
            city = rel.dom_token.word.upper()
            self.procedure_var['D-CITY'] = city_abbrv[city]
            self.pattern_set.append(
                Exp(
                    'FROM-LOC', 
                    self.context['pred'], 
                    Literal('CITY-NAME', 'c1', city)
                )
            )
            self.context['FROM-LOC'] = True
    def add_arrive_city(self):
        sub_rel = filter(lambda rel: rel.rule.name in ['case-a', 'dobj-a'], self.relation_set)
        for rel in sub_rel:
            tok = rel.dom_token if rel.rule.name == 'case-a' else rel.dep_token
            city = tok.word.upper()
            self.procedure_var['A-CITY'] = city_abbrv[city]
            self.pattern_set.append(
                Exp(
                    'TO-LOC',
                    self.context['pred'],
                    Literal('CITY-NAME', 'c2', city)
                )
            )
            self.context['TO-LOC'] = True

    def add_timemod(self):
        sub_rel = filter(lambda rel: rel.rule.name in ['case-t', 'case-t-wh', 'is'], self.relation_set)


        if self.context['FROM-LOC'] and self.context['TO-LOC']:
            qtyp = 'Runtime'
            typ = 'RUN-IN'
            var = 'RUN-TIME'
            name = 'r1'
        elif self.context['FROM-LOC']:
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
                self.procedure_var[var] = timemod

                self.pattern_set.append(
                    Exp(
                        typ,
                        self.context['pred'],
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
                        self.context['pred'],
                        query
                    )
                )


    def add_agent(self):
        sub_rel = filter(lambda rel: rel.rule.name in ['namemod', 'det-wh'], self.relation_set)
        for rel in sub_rel:
            # Normal type
            if rel.rule.name == 'namemod':
                train_name = rel.dep_token.word.upper()
                self.procedure_var['TRAIN'] = train_name
                self.pattern_set.append(
                    Exp(
                        'AGENT',
                        self.context['pred'],
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
                        self.context['pred'],
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
        return self.query_set + self.pattern_set

    def get_logical_form(self):
        queries = ' '.join([str(x) for x in self.query_set])
        attrib = ' '.join([f'({str(pattern)})' for pattern in self.pattern_set])
        return f'({queries}: {attrib})'

class Database:
    def __init__(self, raw_db):
        self.trains = []
        self.atimes = []
        self.dtimes = []
        self.runtimes = []
        for ele in raw_db:
            row = ' '.join(ele.replace('(', '').replace(')', '').split())
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

class Retriever:
    def __init__(self, procedure_var, query_set, context):
        self.procedure_var = procedure_var
        self.query_set = query_set
        
        self.procedure_set = []
        self.context = context


    def get_procedure(self):
        train = self.procedure_var['TRAIN']
        dcity = self.procedure_var['D-CITY']
        acity = self.procedure_var['A-CITY']
        dtime = self.procedure_var['DTIME']
        atime = self.procedure_var['ATIME']
        rtime = self.procedure_var['RUN-TIME']
        for q in self.query_set:
            if isinstance(q, Wh_Query):
                if(q.typ == 'Train'):
                    self.procedure_set.append(
                        Procedure('PRINT-ALL', train)
                    )
                elif(q.typ == 'DTime'):
                    self.procedure_set.append(
                        Procedure('PRINT-ALL', dtime) 
                    )
                elif(q.typ == 'ATime'):
                    self.procedure_set.append(
                        Procedure('PRINT-ALL', atime), 
                    )
                elif(q.typ == 'Runtime'):
                    self.procedure_set.append(
                        Procedure('PRINT-ALL', rtime), 
                    )
            else:
                self.procedure_set.append(Procedure('CHECK-ALL-TRUE', None))

        train_param = f'(TRAIN {train})'
        atime_param = f'(ATIME {train} {acity} {atime})'
        dtime_param = f'(DTIME {train} {dcity} {dtime})'
        rtime_param = f'(RUN-TIME {train} {dcity} {acity} {rtime})'
        
        params  = f'{train_param} {dtime_param} {atime_param} {rtime_param}'

        ret = '\n'.join(f'({str(procedure)} {params})' for procedure in self.procedure_set)

        return ret

    def retrieve(self, procedure, database):
        
        if self.context['FROM-LOC'] and self.context['TO-LOC']:
            related_var = ['TRAIN', 'D-CITY', 'A-CITY', 'RUN-TIME']
            table = database.runtimes
        elif self.context['FROM-LOC']:
            related_var = ['TRAIN', 'D-CITY', 'DTIME']
            table = database.dtimes
        else:
            related_var = ['TRAIN', 'A-CITY', 'ATIME']
            table = database.atimes

        related_var = {k: self.procedure_var[k] for k in related_var if k in related_var}
        
        def matches(row):
            for k, v in related_var.items():
                if '?' not in v and v not in row:
                    return False
            return True

        rows = [row for row in table if matches(row)]

        if procedure.name == 'PRINT-ALL':
            if procedure.var == self.procedure_var['TRAIN']:
                idx = 1
            elif procedure.var in [self.procedure_var['ATIME'], self.procedure_var['DTIME']]:
                idx = 3
            elif procedure.var in [self.procedure_var['RUN-TIME'], self.procedure_var['DTIME']]:
                idx = 4
            else:
                raise Exception('Not Implemented')

            if(len(rows) > 0):
                return ' '.join([row.split()[idx] for row in rows])
            else:
                return 'Không tìm thấy thông tin tàu hỏa'
        else:
            if(len(rows) > 0):
                return 'Có'
            else:
                return 'Không'
    def retrieve_all(self, database):
        ret = []
        for procedure in self.procedure_set:
            ret.append(self.retrieve(procedure, database))
        return '\n'.join(ret)