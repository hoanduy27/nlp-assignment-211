# import regex as re
# import unicodedata
# from lexicon import keywords

# REGEX_SPECIAL = u'*^$*+?!#|\\()[].'
# REGEX_SPECIAL_TRANSLATOR = str.maketrans({ch: f'\\{ch}' for ch in REGEX_SPECIAL})

# def len_reg(r):
#   return len(r[r.find('>') + 1:])

# def remove_accents(text):
#   s1 = u'ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯưẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệỈỉỊịỌọỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰựỲỳỴỵỶỷỸỹ'
#   s0 = u'AAAAEEEIIOOOOUUYaaaaeeeiioooouuyAaDdIiUuOoUuAaAaAaAaAaAaAaAaAaAaAaAaEeEeEeEeEeEeEeEeIiIiOoOoOoOoOoOoOoOoOoOoOoOoUuUuUuUuUuUuUuYyYyYyYy'
#   s = ''
#   for c in text:
#     if c in s1:
#       s += s0[s1.index(c)]
#     else:
#       s += c
#   return s

# def mutate_keyword(word):
#   word = unicodedata.normalize('NFKC', word)
#   word = word.translate(REGEX_SPECIAL_TRANSLATOR)
#   non_accent_word = remove_accents(word)
#   return list(set([
#            word, 
#            non_accent_word, 
#            ''.join(word.split()), 
#            ''.join(non_accent_word.split())
#       ]))

# def make_regex_from_word_list(k, lst, mutation=None): 
#   if mutation is not None:
#     lst_mutate = list(set([word for sublist in list(map(mutation, lst)) for word in sublist]))
#   else:
#     lst_mutate = lst[0:]
#     # print(lst_mutate)
#   lst_mutate = sorted(lst_mutate, key=len, reverse=True)
#   regexps = [fr'(?P<{k}>(?<!\w){el}(?!\w))' for el in lst_mutate]
#   return regexps
  
# def make_regex_from_group_words(group_words, mutation):
#   # token_spec = [(k.replace('-', '_'), make_regex_from_word_list(v, mutation)) for k,v in group_words.items()]
#   # tok_regex = '|'.join(f'(?P<{k}>{v})' for k,v in token_spec)
#   tok_regex = [r for k,v in group_words.items() for r in make_regex_from_word_list(k.replace('-', '_'), v, mutation)]
#   tok_regex = sorted(tok_regex, key=len_reg, reverse=True)
#   tok_regex = '|'.join(tok_regex)
#   r = re.compile(fr'{tok_regex}', flags=re.U|re.I)
#   return r
  

# def tokenize(text):
#   keyword_regex = make_regex_from_group_words(keywords, mutate_keyword) if keywords is not None else None

#   return keyword_regex.sub(lambda m: ' ' + m.lastgroup + ' ', text).split()

# if __name__ == '__main__':
#   texts = [
#     'Tàu hỏa nào đến thành phố Huế lúc 19:00HR ?',
#     'Thời gian tàu hỏa B3 chạy từ Đà Nẵng đến TP. Hồ Chí Minh là mấy giờ ?',
#     'Tàu hỏa nào đến thành phố Hồ Chí Minh ?',
#     'Tàu hỏa nào chạy từ Nha Trang, lúc mấy giờ ?',
#     'Tàu hỏa nào chạy từ Tp. Hồ Chí Minh đến Hà Nội ?',
#     'Tàu hỏa B5 có chạy từ Đà Nẵng không ?'
#   ]
#   for text in texts:
#     print(tokenize(text))
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
