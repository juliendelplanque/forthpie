class WordReference(object):
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return f"{self.__class__.__name__}({self.name})"

class Label(object):
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return f"{self.__class__.__name__}({self.name})"

class LabelReference(object):
    def __init__(self, name):
        self.name = name
        self.resolved_address = None
    
    def __str__(self):
        return f"{self.__class__.__name__}({self.name})"

class Byte(object):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return f"{self.__class__.__name__}({self.value})"

class Align(object):
    pass

class Word(object):
    def __init__(self, name, tokens, compile_only=False, immediate=False):
        self.name = name
        self.tokens = tokens
        self.compile_only = compile_only
        self.immediate = immediate

    def lexicon_bits(self, compiler):
        value = 0
        if self.compile_only:
            value += compiler.COMPILE_ONLY
        if self.immediate:
            value += compiler.IMMEDIATE
        return value

class Primitive(Word):
    def __init__(self, name, **kwargs):
        super().__init__(name, [], **kwargs)
    
    def accept_visitor(self, visitor):
        return visitor.visit_Primitive(self)

class ColonWord(Word):
    def accept_visitor(self, visitor):
        return visitor.visit_ColonWord(self)

class UserVariable(Word):
    def __init__(self, name, cells=1, **kwargs):
        super().__init__(name, [], **kwargs)
        self.cells = cells
    
    def accept_visitor(self, visitor):
        return visitor.visit_UserVariable(self)

class WordsSet(object):
    def __init__(self, name, *args, requirements=[]):
        self.name = name
        self.words = args
        self.requirements = requirements
    
    def __str__(self):
        return f"{self.__class__.__name__}[{self.name}]({[ w.name for w in self.words ]})"
    
    def accept_visitor(self, visitor):
        return visitor.visit_WordsSet(self)

class Image(object):
    def __init__(self, *args):
        self.words_sets = []
        for word_set in args:
            self.add_words_set(word_set)
    
    def add_words_set(self, words_set):
        self.words_sets.append(words_set)
    
    def __str__(self):
        return f"{self.__class__.__name__}({[ ws.name for ws in self.words_sets ]})"
    
    def accept_visitor(self, visitor):
        return visitor.visit_Image(self)

def code(string):
    return [WordReference(s) for s in string.split()] 

def WR(*args):
    if len(args) == 1:
        return WordReference(args[0])
    elif len(args) > 1:
        return [WordReference(s) for s in args]
    else:
        Exception("Can not build WR")

L = Label
LR = LabelReference

class ImageVisitor(object):
    def visit_Image(self, image):
        pass
    
    def visit_WordsSet(self, words_set):
        pass
    
    def visit_UserVariable(self, user_variable):
        pass
    
    def visit_ColonWord(self, colon_word):
        pass
    
    def visit_Primitive(self, primitive):
        pass
