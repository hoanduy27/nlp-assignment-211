from .nlp_grammar import *

class Procedure:
    def __init__(self, name, var):
        self.name = name
        self.var = var
    
    def __str__(self):
        return f'{self.name} {self.var}' if self.var is not None else self.name

    def __repr__(self) -> str:
        return self.__str__()

class Retriever:
    def __init__(self, query_set, context):
        self.query_set = query_set
        
        self.procedure_set = []
        self.context = context


    def get_procedure(self):
        train = self.context.procedure_var['TRAIN']
        dcity = self.context.procedure_var['D-CITY']
        acity = self.context.procedure_var['A-CITY']
        dtime = self.context.procedure_var['DTIME']
        atime = self.context.procedure_var['ATIME']
        rtime = self.context.procedure_var['RUN-TIME']
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
        
        if self.context.from_loc and self.context.to_loc:
            related_var = ['TRAIN', 'D-CITY', 'A-CITY', 'RUN-TIME']
            table = database.runtimes
        elif self.context.from_loc:
            related_var = ['TRAIN', 'D-CITY', 'DTIME']
            table = database.dtimes
        else:
            related_var = ['TRAIN', 'A-CITY', 'ATIME']
            table = database.atimes

        related_var = {k: self.context.procedure_var[k] for k in related_var if k in related_var}
        
        def matches(row):
            for k, v in related_var.items():
                if '?' not in v and v not in row:
                    return False
            return True

        rows = [row for row in table if matches(row)]

        if procedure.name == 'PRINT-ALL':
            if procedure.var == self.context.procedure_var['TRAIN']:
                idx = 1
            elif procedure.var in [self.context.procedure_var['ATIME'], self.context.procedure_var['DTIME']]:
                idx = 3
            elif procedure.var in [self.context.procedure_var['RUN-TIME'], self.context.procedure_var['DTIME']]:
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