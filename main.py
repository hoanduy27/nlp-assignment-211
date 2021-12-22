import os
import nltk

import argparse
from Models.tokenization import tokenize
from Models.parsing_rule import leftarcs, rightarcs
from Models.dep_parse import DependencyParsing
from Models.grammatical_relation import GrammaticalRelation

def write_output(name, content):
    with open(os.path.join(os.path.dirname(__file__), f'Output/output_{name}.txt'), 'w') as f:
        f.write(content)

def main(args):
    """
    Main entry point for the program
    """
    question_file = os.path.join(os.path.dirname(__file__), args.question_file)
    grammar_path = os.path.join(os.path.dirname(__file__), args.grammar_path)
    question = open(question_file, 'r').read()
    question = question.replace(',', '')
    verbose = args.verbose

    print(question)
    print("-------------Tokenization---------------------")
    buffer = tokenize(grammar_path, question)
    write_output('a', '\n'.join([str(b) for b in buffer]))
    print(buffer)
    
    print("-------------Dependency Parsing---------------------")
    dep = DependencyParsing(leftarcs, rightarcs ,buffer, verbose)
    relation_set = dep.parse()
    write_output('b', '\n'.join([str(r) for r in relation_set]))
    print(relation_set)

    print("-------------Grammatical Relation---------------------")
    grammar_relation_gen = GrammaticalRelation(relation_set)
    grammar_relation_gen.generate()
    grammar_relation = grammar_relation_gen.get_grammatical_relation()
    write_output('c', '\n'.join([str(f'({r})') for r in grammar_relation]))
    print(grammar_relation)

    print("-------------Logical form---------------------")
    logical_form = grammar_relation_gen.get_logical_form()
    write_output('d', logical_form)
    print(logical_form)

    print("-------------Procedure---------------------")
    procedure = grammar_relation_gen.get_procedure()
    write_output('d', procedure)
    print(procedure)
    
    
    

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='NLP Assignment 2021')
    parser.add_argument(
        '--question-file', 
        type=str, 
        default='Input/input_1.txt', 
        help='Path to question file. Default: Input/input_1.txt'
    )

    # parser.add_argument(
    #     '--question', 
    #     type=str, 
    #     default='Tàu hỏa nào đến thành phố Huế lúc 19:00HR ?', 
    #     help='Question to be parsed. Default: Tàu hỏa nào đến thành phố Huế lúc 19:00HR ?'
    # )

    parser.add_argument(
        '--grammar-path',
        type=str,
        default='Models/grammar.cfg',
        help='Path to grammar. Default: Models/grammar.cfg'
    )

    parser.add_argument(
        '--verbose',
        type=int,
        default=0,
        help='Verbose mode. Default: 0'
    )
    args = parser.parse_args()
    main(args)