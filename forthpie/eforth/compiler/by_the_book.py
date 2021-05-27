from ...compiler import AbstractCompiler, CompilerMetadata, WordMetaData, WordNotInDictionary
from ...model import WordReference, Label, LabelReference, Byte, Align

class Compiler(AbstractCompiler):
    """Compiler for the EForth dictionary format.
    """
    COMPILE_ONLY = 0x040
    IMMEDIATE = 0x080
    LEXICON_MASK = 0x07F1F # Cell with all bits at 1 except meta-data bits.

    def __init__(self, cell_size, initial_code_address, initial_name_address, initial_user_address, memory, primitives_provider):
        self.cell_size = cell_size
        self.code_address = initial_code_address
        self.name_address = initial_name_address
        self.user_address = initial_user_address
        self.memory = memory
        self.primitives_provider = primitives_provider
        self._compiler_metadata = CompilerMetadata(initial_user_address)

    @property
    def compiler_metadata(self):
        self._compiler_metadata.user_address = self.user_address
        return self._compiler_metadata

    def get_primitive_by_name(self, name):
        return self.primitives_provider.get_primitive_by_name(name)

    def read_word_name(self, name_token_address):
        """Reads the name of the word encoded in the name token which first
        address is name_token_address.

        Args:
            name_token_address (int): Address of the name token in memory.

        Returns:
            str: Name of the word.
        """
        name_length = self.memory[name_token_address+2*self.cell_size] & self.LEXICON_MASK
        name_first_address = name_token_address+2*self.cell_size+1
        return "".join([ chr(c) for c in self.memory[name_first_address:name_first_address+name_length] ])

    def read_previous_name_token_address(self, name_token_address):
        """Read the address of the previous name token from the name token
        stored at name_token_address.

        Args:
            name_token_address (int): Address of the name token to read
                                      previous token from.

        Returns:
            int: Address of the previous name token.
        """
        return self.read_cell_at_address(name_token_address+self.cell_size) - 2 * self.cell_size # NOTE: I modified this

    def read_execution_token_address(self, name_token_address):
        """Read the address of the execution token from the name token
        stored at name_token_address.

        Args:
            name_token_address (int): Address of the name token to read
                                      previous token from.

        Returns:
            int: Address of the execution token.
        """
        return self.read_cell_at_address(name_token_address)

    def name_tokens_iterator(self):
        """Returns an iterator on the name dictionary.
        This iterator yields address of the name dictionary entries.
        Pay attention that the address that are yield by this iterator point
        to the first address in memory used by the entry (and not the address
        of the meta-data byte which is the address referenced by the Link
        field in the entry).

        Yields:
            int: Addresses of name tokens.
        """
        current_address = self.name_address
        while current_address != 0:
            yield current_address
            current_address = self.read_previous_name_token_address(current_address)

    def name_token(self, word_reference):
        """Retrieve the name token from a word_reference object and returns it.

        Args:
            word_reference (WordReference): The word reference to retrieve the
            name token from.

        Raises:
            WordNotInDictionary: When the word searched does not exist in the
                                 directory.

        Returns:
            int: The address of the name token found.
        """
        for name_token in self.name_tokens_iterator():
            if self.read_word_name(name_token) == word_reference.name:
                return name_token

        raise WordNotInDictionary(word_reference.name)

    def lookup_word(self, word_reference):
        """Lookup a word execution token from a word_reference object and returns it.
        """
        # Check if word exists in already defined words
        try:
            return self.read_execution_token_address(self.name_token(word_reference))
        except WordNotInDictionary:
            # Else, check if exists in primitives (a primitive is always defined before any high-level word, so they need to be searched after them.).
            return self.get_primitive_by_name(word_reference.name).code

    def lexicon_bits(self, compile_only, immediate):
        """Create a byte encoding lexicon bits COMPILE_ONLY and IMMEDIATE.

        Args:
            compile_only (bool): Should the word be compile only?
            immediate (bool): Should the word be immediate ?

        Returns:
            int: A byte encoding compile only and immediate flags.
        """
        value = 0
        if compile_only:
            value += self.COMPILE_ONLY
        if immediate:
            value += self.IMMEDIATE
        return value

    def compile_name_header(self, compile_only, immediate, name):
        """Compile a code definition header.

        From EForth and Zen, the format of an entry in the name dictionary is
        the following (I added some implicit information to the original table):

        Field     Length           Function
        -----------------------------------------------------------
        Token     cell-size bytes  code address (ca)
        Link      cell-size bytes  name address (na) of previous word, this is
                                   the address of the meta-data byte of
                                   previous name dictionary entry.
        Length    1 byte           lexicon bits (3 bits) and
                                   length of Name (5bits)
        Name      n bytes          name of word number of bytes depends on
                                   Length field
        Filler    0/cell-size byte fill to cell boundary

        Args:
            compile_only (bool): Should the word be compile only?
            immediate (bool): Should the word be immediate?
            name (str): Name of the word.

        Raises:
            Exception: [description]
        """
        self.code_address = self.align_address(self.code_address)
        code_address = self.code_address
        previous_name_address = self.name_address
        name_length = len(name)
        if name_length > 0b11111:
            raise Exception("Name too long, can not be compiled.")

        metadataByte = name_length | self.lexicon_bits(compile_only, immediate)
        self.name_address -= name_length + 3 * self.cell_size

        self.write_cell_at_address(self.name_address, code_address)
        self.write_cell_at_address(self.name_address+self.cell_size, previous_name_address+2*self.cell_size)
        self.memory[self.name_address+2*self.cell_size] = metadataByte
        name_start_address = self.name_address+2*self.cell_size+1
        name_stop_address = self.name_address+2*self.cell_size+1+name_length
        for address, letter in zip(range(name_start_address, name_stop_address), name):
            self.memory[address] = ord(letter)

    def compile_code_header(self, compile_only, immediate, name, primitive_name):
        """Compile a colon definition header.

        Args:
            compile_only (bool): Should the word be compile only?
            immediate (bool): Should the word be immediate?
            name (str): Name of the word.
            primitive_name (str): The name of the primitive to use as first
                                  token in the word thread.
        """
        self.compile_name_header(compile_only, immediate, name)
        self.compiler_metadata.add_word_meta(WordMetaData(name, self.code_address))
        self.write_cell_at_address(self.code_address, self.get_primitive_by_name(primitive_name).code)
        self.code_address += self.cell_size

    def compile_primitive(self, name, compile_only=False, immediate=False):
        """Compile a primitive definition.

        Args:
            name (str): Name of the primitive word.
            compile_only (bool): Should the word be compile only?
            immediate (bool): Should the word be immediate?
        """
        self.compile_code_header(compile_only, immediate, name, name)
        self.compiler_metadata.last().end_address = self.code_address-self.cell_size

    def compile_colon_header(self, compile_only, immediate, name):
        """Compile a colon definition header.

        Args:
            compile_only ([type]): [description]
            immediate ([type]): [description]
            name ([type]): [description]
        """
        self.compile_code_header(compile_only, immediate, name, "doLIST")

    def compile_user_header(self, compile_only, immediate, name):
        """Compile a user variable header.
        """
        self.compile_colon_header(compile_only, immediate, name)
        self.write_cell_at_address(self.code_address, self.lookup_word(WordReference("doUSER")))
        self.code_address += self.cell_size
        self.write_cell_at_address(self.code_address, self.user_address)
        self.code_address += self.cell_size
        self.user_address += self.cell_size

    def compile_user(self, name, compile_only=False, immediate=False, cells=1):
        self.compile_user_header(compile_only, immediate, name)
        self.user_address += (cells-1)*self.cell_size
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
                code_address_for_label_resolution += len(token)+1 # +1 for size of str
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
                # Ensure instruction alignment.
                self.code_address = self.align_address(self.code_address)
            elif isinstance(token, int):
                for i, b in enumerate(token.to_bytes(self.cell_size, "little", signed=True)):
                    self.memory[self.code_address+i] = b
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

    def compile_colon(self, name, tokens, compile_only=False, immediate=False):
        self.compile_colon_header(compile_only, immediate, name)
        self.compile_word_body(tokens)
        self.compiler_metadata.last().end_address = self.code_address-self.cell_size
