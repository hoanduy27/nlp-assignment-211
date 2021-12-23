import os
import argparse

from Models.nlp_utils import Printout, tokenize, Database
from Models.parsing_rule import leftarcs, rightarcs

from Models.nlp_parser import DependencyParsing
from Models.nlp_grammar import GrammaticalRelation
from Models.nlp_retriever import Retriever

def write_output(name, content):
    with open(os.path.join(os.path.dirname(__file__), f'Output/output_{name}.txt'), 'w') as f:
        f.write(content)

def main(args):
    """
    Main entry point for the program
    """
    verbose = args.verbose
    printout = Printout([], verbose)
    try:
        question_path = os.path.join(os.path.dirname(__file__), args.question_path)
        question = open(question_path, 'r').read()
        
        printout.print(f'>>> Query: {question}\n')
    except:
        question = args.question_text
        
        printout.print(f'>>> Query: {question}\n')

    grammar_path = os.path.join(os.path.dirname(__file__), args.grammar_path)
    database = Database(
        os.path.join(os.path.dirname(__file__), args.database_path)
    )
    
    
    question = question.replace(',', '')
    
    printout.print(f'>>> DATABASE:\n{str(database)}\n')
    printout.print('>>> Trace:')
    printout.print("-------------Tokenization---------------------")
    buffer = tokenize(grammar_path, question)
    # write_output('a', '\n'.join([str(b) for b in buffer]))
    
    printout.print([b.word for b in buffer])
    printout.print("-------------Dependency Parsing---------------------")

    dep = DependencyParsing(leftarcs, rightarcs ,buffer, verbose-1)
    relation_set, logs = dep.parse()

    relation_set_str = '\n'.join([str(r) for r in relation_set])
    write_output('b', relation_set_str)

    if verbose > 1:
        printout.print(str(logs) )

    printout.print(relation_set_str)
    printout.print("-------------Grammatical Relation---------------------")

    grammar_relation_gen = GrammaticalRelation(relation_set)
    grammar_relation_gen.generate()
    grammar_relation = grammar_relation_gen.get_grammatical_relation()

    write_output('c', grammar_relation)
    
    printout.print(grammar_relation)
    printout.print("-------------Logical form---------------------")

    logical_form = grammar_relation_gen.get_logical_form()
    write_output('d', logical_form)
    
    printout.print(logical_form)
    printout.print("-------------Procedure---------------------")

    query_set = grammar_relation_gen.query_set
    context = grammar_relation_gen.context

    retriever = Retriever(query_set, context)

    procedure = retriever.get_procedure()
    write_output('e', procedure)
    printout.print(procedure)

    printout.print("-------------Retrieval---------------------")
    result = retriever.retrieve_all(database)
    write_output('f', result)
    printout.print(result)


    print(printout)
if __name__=='__main__':
    parser = argparse.ArgumentParser(description='NLP Assignment 2021')

    question_group = parser.add_mutually_exclusive_group(required=True)
    
    question_group.add_argument(
        '--question-path', 
        type=str, 
        help='Path to question file'
    )

    question_group.add_argument(
        '--question-text',
        type=str,
        help='Question text'
    )

    parser.add_argument(
        '--grammar-path',
        type=str,
        default='Models/grammar.cfg',
        help='Path to grammar for tokenization. Default: Models/grammar.cfg'
    )

    parser.add_argument(
        '--database-path',
        type=str,
        default='Input/db.txt',
        help='Path to database. Default: Input/db.txt'
    )

    parser.add_argument(
        '--verbose',
        type=int,
        default=0,
        help='Verbose mode. Default: 0'
    )
   
    args = parser.parse_args()
    main(args)