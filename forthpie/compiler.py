from .forth import *

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
    def __init__(self):
        self.words_metadata = []
    
    def add_word_meta(self, word_meta):
        self.words_metadata.append(word_meta)
    
    def last(self):
        return self.words_metadata[-1]
    
    def word_address_belongs_to(self, address):
        return next(m for m in self.words_metadata if m.is_part_of_code(address))

class Compiler(MemoryManipulator):
    COMPILE_ONLY = 0x040
    IMMEDIATE = 0x080

    def __init__(self, cell_size, initial_code_address, initial_name_address, initial_user_address, memory, primitives_provider=ForthInterpreter):
        self.cell_size = cell_size
        self.code_address = initial_code_address
        self.name_address = initial_name_address
        self.user_address = initial_user_address
        self.memory = memory
        self.primitives_provider = primitives_provider
        self.compiler_metadata = CompilerMetadata()
    
    def get_primitive_by_name(self, name):
        return self.primitives_provider.get_primitive_by_name(name)

    def read_word_name(self, name_token_address):
        name_length = self.memory[name_token_address+2*self.cell_size] & 0b11111
        name_first_address = name_token_address+2*self.cell_size+1
        return "".join([ chr(c) for c in self.memory[name_first_address:name_first_address+name_length] ])
    
    def read_previous_name_token_address(self, name_token_address):
        return self.read_cell_at_address(name_token_address+self.cell_size) - 2 * self.cell_size # NOTE: I modified this
    
    def read_execution_token_address(self, name_token_address):
        return self.read_cell_at_address(name_token_address)
    
    def name_tokens_iterator(self):
        current_address = self.name_address
        while current_address != 0:
            yield current_address
            current_address = self.read_previous_name_token_address(current_address)
    
    def name_token(self, word_reference):
        """Retrieve the name token from a word_reference object and returns it.
        """
        current_address = self.name_address
        while current_address != 0 and self.read_word_name(current_address) != word_reference.name:
            current_address = self.read_previous_name_token_address(current_address)
        
        if self.read_word_name(current_address) == word_reference.name:
            return self.read_execution_token_address(current_address)
        
        raise WordNotInDictionary(word_reference.name)
    
    def lookup_word(self, word_reference):
        """Lookup a word execution token from a word_reference object and returns it.
        """
        # Check if word exists in already defined words
        try:
            return self.name_token(word_reference)
        except WordNotInDictionary:
            # Else, check if exists in primitives (a primitive is always defined before any high-level word, so they need to be searched after them.).
            return self.get_primitive_by_name(word_reference.name).code

    def compile_name_header(self, lexicon_bits, name):
        """Compile a code definition header.

        From EForth and Zen, the format of an entry in the name dictionary is
        the following (I added some implicit information to the original table):

        Field     Length           Function
        -----------------------------------------------------------
        Token     cell-size bytes  code address (ca)
        Link      cell-size bytes  name address (na) of previous word
        Length    1 byte           lexicon bits (3 bits) and length of Name (5bits)
        Name      n bytes          name of word number of bytes depends on Length field
        Filler    0/cell-size byte fill to cell boundary 
        """
        self.code_address = self.align_address(self.code_address)
        code_address = self.code_address
        previous_name_address = self.name_address
        name_length = len(name)
        if name_length > 0b11111:
            raise Exception("Name too long, can not be compiled.")
        # if lexicon_bits > 0b111:
        #     raise Exception("Only 3 bits are available for lexicon bits.")
        
        metadataByte = name_length | lexicon_bits
        # bytes_to_allocate = (2 * self.cell_size) + 1 + name_length
        # padding = self.cell_size - (bytes_to_allocate % self.cell_size)
        # self.name_address -= (bytes_to_allocate + padding)
        self.name_address -= (name_length + 3) * self.cell_size

        self.write_cell_at_address(self.name_address, code_address)
        self.write_cell_at_address(self.name_address+self.cell_size, previous_name_address+2*self.cell_size) # NOTE: I modified this
        self.memory[self.name_address+2*self.cell_size] = metadataByte
        for address, letter in zip(range(self.name_address+2*self.cell_size+1, self.name_address+2*self.cell_size+1+name_length), name):
            self.memory[address] = ord(letter)

    def compile_code_header(self, lexicon_bits, name, primitive_name):
        """Compile a colon definition header.
        """
        self.compile_name_header(lexicon_bits, name)
        # print(f"{name}: xt={self.code_address}")
        self.compiler_metadata.add_word_meta(WordMetaData(name, self.code_address))
        self.write_cell_at_address(self.code_address, self.get_primitive_by_name(primitive_name).code)
        self.code_address += self.cell_size
    
    def compile_primitive(self, name, lexicon_bits=0):
        self.compile_code_header(lexicon_bits, name, name)
        self.compiler_metadata.last().end_address = self.code_address-self.cell_size

    def compile_colon_header(self, lexicon_bits, name):
        """Compile a colon definition header.
        """
        self.compile_code_header(lexicon_bits, name, "doLIST")
    
    def compile_user_header(self, lexicon_bits, name):
        """Compile a user variable header.
        """
        self.compile_colon_header(lexicon_bits, name)
        self.write_cell_at_address(self.code_address, self.lookup_word(WordReference("doUSER")))
        self.code_address += self.cell_size
        self.write_cell_at_address(self.code_address, self.user_address)
        self.code_address += self.cell_size
        self.user_address += self.cell_size
    
    def compile_user(self, name, lexicon_bits=0, cells=1):
        self.compile_user_header(lexicon_bits, name)
        for _ in range(cells-1):
            self.user_address += self.cell_size
        self.compiler_metadata.last().end_address = self.code_address-self.cell_size
    
    def align_address(self, address):
        if address % self.cell_size == 0:
            return address

        return address + (self.cell_size - (address % self.cell_size))

    def compile_word_body(self, tokens):
        label_addresses = dict()
        code_address_for_label_resolution = self.code_address
        for token in tokens:
            if isinstance(token, Label):
                label_addresses[token.name] = code_address_for_label_resolution
            elif isinstance(token, str):
                code_address_for_label_resolution += len(token)+1 #+1 for size of str
                code_address_for_label_resolution = self.align_address(code_address_for_label_resolution)
            elif isinstance(token, Byte):
                code_address_for_label_resolution += 1
            else:
                code_address_for_label_resolution += self.cell_size

        for token in tokens:
            if isinstance(token, str):
                self.memory[self.code_address] = len(token)
                self.code_address += 1
                for c in token:
                    self.memory[self.code_address] = ord(c)
                    self.code_address += 1
                # Ensure instruction alignment. TODO: see if needed
                self.code_address = self.align_address(self.code_address)
            elif isinstance(token, int):
                for i, b in enumerate(token.to_bytes(self.cell_size, "little", signed=True)):
                    self.memory[self.code_address+i] = b
                # self.write_cell_at_address(self.code_address, token)
                self.code_address += self.cell_size
            elif isinstance(token, WordReference):
                address = self.lookup_word(token)
                self.write_cell_at_address(self.code_address, address)
                self.code_address += self.cell_size
            elif isinstance(token, Label):
                pass #ignore
            elif isinstance(token, LabelReference):
                self.write_cell_at_address(self.code_address, label_addresses[token.name])
                self.code_address += self.cell_size
            elif isinstance(token, Byte):
                self.memory[self.code_address] = token.value
                self.code_address += 1
            elif isinstance(token, Align):
                self.code_address = self.align_address(self.code_address)
            else:
                raise Exception(f"Unknown token: {token}")
    
    def compile_colon(self, name, tokens, lexicon_bits=0):
        self.compile_colon_header(lexicon_bits, name)
        self.compile_word_body(tokens)
        self.compiler_metadata.last().end_address = self.code_address-self.cell_size
