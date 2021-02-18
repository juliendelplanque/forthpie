from .by_the_book import *

def by_the_book_optimized_eforth_image(start_of_data_stack_address,
                             start_of_return_stack_address,
                             start_of_user_area_address, # UPP
                             number_of_vocabularies, # VOCCS
                             cell_size,
                             lexicon_mask,
                             immediate_bit,
                             compile_only_bit,
                             doLISTCode,
                             version_number,
                             terminal_input_buffer_address,
                             cold_boot_address):
    image = Image(
        by_the_book_primitives(),
        by_the_book_system_and_user_variables(start_of_user_area_address, number_of_vocabularies),
        by_the_book_common_words(),
        by_the_book_comparison_words(),
        by_the_book_divide_words(),
        by_the_book_multiply_words(),
        by_the_book_memory_alignment_words(cell_size),
        by_the_book_memory_access_words(cell_size),
        by_the_book_numeric_output_single_precision_words(),
        by_the_book_numeric_input_single_precision_words(),
        by_the_book_basic_io_words(),
        by_the_book_parsing_words(),
        by_the_book_dictionary_search_words(lexicon_mask, cell_size),
        by_the_book_terminal_response_words(),
        by_the_book_error_handling_words(),
        by_the_book_text_interpreter_words(compile_only_bit),
        by_the_book_shell_words(terminal_input_buffer_address),
        by_the_book_compiler_words(),
        by_the_book_structure_words(),
        by_the_book_name_compiler_words(),
        by_the_book_forth_compiler_words(immediate_bit, doLISTCode),
        by_the_book_defining_words(doLISTCode),
        by_the_book_tools_words(),
        memory_initializer=by_the_book_memory_initialization(
            start_of_data_stack_address,
            start_of_return_stack_address,
            terminal_input_buffer_address,
            number_of_vocabularies,
            cold_boot_address)
    )

    image.add_words_set(
        by_the_book_hardware_reset_words(
            version_number,
            sum(uv.cells for uv in image.user_variables)+4,
            cell_size,
            start_of_user_area_address,
            cold_boot_address
        )
    )

    return image