from .forth import *
from .model import ImageVisitor

class WordNotInDictionary(Exception):
    def __init__(self, name):
        self.name = name

class WordMetaData(object):
    def __init__(self, word_name, start_address, end_address=None):
        self.name = word_name
        self.start_address = start_address
        self.end_address = end_address

    def is_part_of_code(self, address):
        return self.start_address <= address and address <= self.end_address

class CompilerMetadata(object):
    def __init__(self, start_of_user_area):
        self.words_metadata = []
        self.start_of_user_area = start_of_user_area
        self.user_address = self.start_of_user_area

    def add_word_meta(self, word_meta):
        self.words_metadata.append(word_meta)

    def last(self):
        return self.words_metadata[-1]

    def word_address_belongs_to(self, address):
        return next(m for m in self.words_metadata if m.is_part_of_code(address))

class AbstractCompiler(MemoryManipulator):
    def compile_primitive(self, name, compile_only=False, immediate=False):
        raise NotImplementedError()

    def compile_user(self, name, compile_only=False, immediate=False, cells=1):
        raise NotImplementedError()

    def compile_colon(self, name, tokens, compile_only=False, immediate=False):
        raise NotImplementedError()

class ImageCompiler(ImageVisitor):
    def __init__(self, compiler):
        super().__init__()
        self.compiler = compiler

    def visit_Image(self, image):
        for word_set in image:
            word_set.accept_visitor(self)
        image.initialize_memory(self.compiler)

    def visit_WordsSet(self, words_set):
        for word in words_set:
            word.accept_visitor(self)

    def visit_UserVariable(self, user_variable):
        self.compiler.compile_user(
            name=user_variable.name,
            compile_only=user_variable.compile_only,
            immediate=user_variable.immediate,
            cells=user_variable.cells
        )

    def visit_ColonWord(self, colon_word):
        self.compiler.compile_colon(
            name=colon_word.name,
            tokens=colon_word.tokens,
            compile_only=colon_word.compile_only,
            immediate=colon_word.immediate
        )

    def visit_Primitive(self, primitive):
        self.compiler.compile_primitive(
            name=primitive.name,
            compile_only=primitive.compile_only,
            immediate=primitive.immediate
        )
