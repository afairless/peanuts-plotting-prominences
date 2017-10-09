#! /usr/bin/env python3


def get_sibling_directory_path(sibling_directory_name):
    '''
    returns path for a specified folder that is in the same parent directory as
        the current working directory
    '''

    import os

    current_path = os.getcwd()
    last_separator_position = current_path.rfind(os.sep)
    parent_directory_path = current_path[0:last_separator_position]
    sibling_directory_path = os.path.join(parent_directory_path,
                                          sibling_directory_name)
    return(sibling_directory_path)


def print_intermittent_status_message_in_loop(iteration, every_xth_iteration,
                                              total_iterations):
    '''
    Prints message updating loop's progress for user
    '''

    if iteration % every_xth_iteration == 0:
        print('Processing file {0} of {1}, which is {2:.0f}%'
            .format(iteration + 1, total_iterations,
                    100 * (iteration + 1) / total_iterations))


def read_table(table_filepath, column_of_lists):
    '''
    reads table from 'csv' file
    each item in column 'column_of_lists' is read as a list; as currently
        written, the function can read only 1 column as a list
    '''

    import pandas as pd
    from ast import literal_eval

    # '^' used as separator because it does not appear in any text descriptions
    table = pd.read_csv(table_filepath, sep='^',
                        converters={column_of_lists[0]: literal_eval,
                                    column_of_lists[1]: literal_eval,
                                    column_of_lists[2]: literal_eval})
    return(table)


def read_text_file(text_filename, as_string=False):
    '''
    reads each line in a text file as a list item and returns list by default
    if 'as_string' is 'True', reads entire text file as a single string
    '''

    text_list = []

    try:
        with open(text_filename) as text:
            if as_string:
                # reads text file as single string
                text_list = text.read().replace('\n', '')
            else:
                # reads each line of text file as item in a list
                for line in text:
                    text_list.append(line.rstrip('\n'))
            text.close()
        return(text_list)

    except:
        return('There was an error while trying to read the file')


def write_list_to_text_file(a_list, text_file_name, overwrite_or_append='a'):
    '''
    writes a list of strings to a text file
    appends by default; change to overwriting by setting to 'w' instead of 'a'
    '''

    try:
        textfile = open(text_file_name, overwrite_or_append, encoding='utf-8')
        for element in a_list:
            textfile.write(element)
            textfile.write('\n')

    finally:
        textfile.close()


def add_possessives_to_word_list(word_list):
    '''
    Adds an apostrophe and 's' to each element in 'word_list', then adds each of
        these possessives to the original 'word_list' immediately after the
        corresponding word
    '''

    possessives = [s + '\'s' for s in word_list]
    words_with_poss = [None] * (len(word_list) * 2)
    words_with_poss[::2] = word_list
    words_with_poss[1::2] = possessives

    return(words_with_poss)


def tally_word_counts_in_column(table_column, word_list, output_len):
    '''
    Inputs:  'table_column' is a Pandas DataSeries where each element is a
        string (or list of strings) to be searched; 'word_list' is a list of
        words to search for; 'output_len' is the length of the output table
        'tallies'
    Outputs:  a table/DataFrame with each element in 'word_list' as a column
        name, each row corresponding to each element in 'table_column', and
        values of '0' or '1' indicating whether that column's 'word_list'
        element appeared in that row's 'table_column' element; '0' is 'No' and
        '1' is 'Yes'
    'word_list' elements that are single words must match a token from the
        'table_column' string to be considered a match; this prevents words from
        matching when they are only sub-words in the string (e.g., so that
        searching for 'hat' in 'that' does not yield a match);
    'word_list' elements that are multiple words or hyphenated are searched for
        in the string itself (which can produce the sub-word problem described
        above)
    '''

    import pandas as pd
    from numpy import arange
    from enchant.tokenize import get_tokenizer

    tallies = pd.DataFrame(0, index=arange(output_len), columns=word_list)
    tokenizer = get_tokenizer('en_US')
    message_interval = 1000

    for i, text in table_column.iteritems():

        print_intermittent_status_message_in_loop(i, message_interval,
                                                  output_len)

        if isinstance(text, list):  # if text stored in list instead of string
            if not text[0] and len(text) == 1:
                continue            # skips empty lists
            text = ' '.join(text)

        tokens = [w[0].lower() for w in tokenizer(text)]

        for j in range(len(word_list)):

            if (' ' in word_list[j]) or ('-' in word_list[j]):
                if word_list[j] in text:
                    tallies.iloc[i, j] = 1
            else:
                if word_list[j] in tokens:
                    tallies.iloc[i, j] = 1

    return(tallies)


def combine_column_pairs(table):
    '''
    Combines each adjacent pair of columns in a dataframe with Boolean 'or' and
        returns the new table (with half the number of columns as the original
        table)
    '''

    import numpy as np
    import pandas as pd

    columns = table.columns.values.tolist()
    columns = columns[0::2]     # excludes every other element
    combined_table = pd.DataFrame(0, index=np.arange(len(table)),
                                  columns=columns)

    for i in range(len(columns)):
        combined_table.iloc[:, i] = table.iloc[:, i*2] | table.iloc[:, i*2+1]

    return(combined_table)


def count_characters(expanded_table, characters):
    '''
    Performs a series of counts; each count tallies when words from 'characters'
        appear in a specified column from 'expanded_table'
    Each count is returned as a table/Pandas DataFrame; each word in
        'characters' has its own column; each element from the column in
        'expanded_table' has its own row; if a word appears in a column element,
        the value is '1', otherwise it's '0'
    Output:  Each count table is stored as an element in the list 'counts'
    '''

    columns_to_count = [expanded_table.ix[:, 'text_spell_corrected'],         # for an overall count
                        expanded_table.ix[:, 'text_nontalk'],                 # count in text outside double-quotes
                        expanded_table.ix[:, 'text_talk'],                    # count in text inside double-quotes
                        expanded_table.ix[expanded_table['odd_quotes'] == 1,  # counts text with odd number of double-quotes
                                          'text_spell_corrected'],
                        expanded_table.ix[expanded_table['no_quotes'] == 1,   # counts text with no double-quotes
                                          'text_spell_corrected']]
    counts = []

    for i in range(len(columns_to_count)):
        temp = tally_word_counts_in_column(columns_to_count[i], characters,
                                           len(expanded_table))
        counts.append(combine_column_pairs(temp))

    return(counts)


def counts_summary_table(counts):
    '''
    Returns table of counts for each searched-for word (usually characters),
        with one word per row; columns show different counts based on which
        text was counted
    '''

    import pandas as pd

    a = counts[0].sum()     # overall count, from 'text_spell_corrected' column
    b = counts[1].sum()     # 'nontalk' count from 'text_nontalk' column
    c = counts[2].sum()     # 'talk' count from 'text_talk' column
    d = counts[3].sum()     # 'odd_quotes' count from text panels with an odd number of double-quotes
    e = counts[4].sum()     # 'no_quotes' count from text panels with no double-quotes

    f = (counts[1] | counts[2] | counts[3] | counts[4]).sum()   # sums everything except 'overall'; should be identical to 'overall'

    sums = pd.DataFrame(data=[a, b + e, c, d, f]).transpose()   # b + e:  'no_quotes' is classified as 'nontalk'
    sums.columns = ['overall', 'nontalk', 'talk', 'oddq', 'sum']
    sums['error'] = ((sums['sum'] / sums['overall']) * 100) - 100  # verify that 'overall' matches 'sum', errors = 0

    return(sums)


def characters_merge_dict():
    '''
    Creates dictionary of keys naming characters and values of the names that
        the keys should be reclassified under; this allows the data associated
        with the keys to be associated with the value
    '''

    chars = {'charlie'                      : 'charlie brown',
             'brown'                        : 'charlie brown',
             'charles'                      : 'charlie brown',
             'lucy van pelt'                : 'lucy',
             'linus van pelt'               : 'linus',
             'sally brown'                  : 'sally',
             'peggy-jean'                   : 'peggy jean',
             'pig pen'                      : 'pig-pen',
             'pigpen'                       : 'pig-pen',
             'beagle scout'                 : 'beaglescout',
             'beagle-scout'                 : 'beaglescout',
             'beagle scouts'                : 'beaglescouts',
             'beagle-scouts'                : 'beaglescouts',
             'shlabotnik'                   : 'joe shlabotnik',
             'molly'                        : 'molly volley',
             'charlotte'                    : 'charlotte braun',
             'braun'                        : 'charlotte braun',
             'crybaby'                      : 'crybaby boobie',
             'boobie'                       : 'crybaby boobie',
             'tapioca'                      : 'tapioca pudding',
             'red haired girl'              : 'red-haired girl',
             'sweetstory'                   : 'helen sweetstory',
             'pig-tailed girl'              : 'pigtailed girl',
             'pig tailed girl'              : 'pigtailed girl',
             'kindergarten friend'          : 'pigtailed girl',
             'school building'              : 'the school building',
             'school thinks'                : 'the school building',
             'world-famous'                 : 'world famous',
             'world-famous grocery clerk'   : 'world famous grocery clerk',
             'world-famous golf'            : 'world famous golf',
             'legionnaires'                 : 'legionnaire',
             'kite-eating'                  : 'kite-eating tree',
             'kite eating tree'             : 'kite-eating tree'}

    return(chars)


def merge_two_columns(count_table, col1_name, col2_name, merged_name):
    '''
    Replaces two columns in a Pandas DataFrame with new column created by a
        Boolean disjunction ('or') of the original two columns
    '''

    col1 = count_table[col1_name]
    col2 = count_table[col2_name]

    count_table.drop(col1_name, axis=1, inplace=True)
    count_table.drop(col2_name, axis=1, inplace=True)
    count_table[merged_name] = col1 | col2

    return(count_table)


def find_two_columns_to_merge(column_names, merge_dict):
    '''
    searches in 'column_names' for the names of two columns to be merged
    a column should be merged if it's a key in 'merge_dict'; the key's value
        is the new name for the merged column
    if the new name is itself already a column, the column should be merged
        with this existing 'new name' column
    if the new name is not already a column, then search for a 2nd column that
        has the same new name listed as a value in 'merge_dict' as the 1st
        column did; if such a 2nd column is found, merge the 1st and 2nd columns
        under the shared new name
    returns the names of the two columns to be merged and the new name for the
        merged column
    '''

    for i in range(len(column_names)):

        col1_name = column_names[i]

        if col1_name not in merge_dict:
            continue

        # find a column in 'merge_dict' to be merged; identify its new, merged name
        col1_new_name = merge_dict[col1_name]

        # if the new name is already a column
        if col1_new_name in column_names:

            # merge the two columns together under the new name
            return(col1_name, col1_new_name, col1_new_name)

        # if the new name is not already a column
        else:

            # find a 2nd column...
            for j in range(i + 1, len(column_names)):

                col2_name = column_names[j]

                # ...that should be merged...
                if col2_name in merge_dict:

                    col2_new_name = merge_dict[col2_name]

                    # ...and has same new name as the 1st column
                    if col1_new_name == col2_new_name:

                        # merge the two columns together under the shared new name
                        return(col1_name, col2_name, col1_new_name)

                    else:
                        continue

    # if no columns are found, return empty strings
    return('', '', '')


def merge_character_counts_into_single_columns(count_table):
    '''
    Inputs:  'count_table' is a table/Pandas DataFrame that tallies whether a
        word or phrase (naming characters) appeared in items of text; each word
        has its own column; each row corresponds to an item of text; if a word
        appeared in a text item, the corresponding cell in the 'count_table'
        is '1', otherwise it's '0'
    Merges columns in 'count_table' as specified in the dictionary
        'characters_merge', which names the columns to be merged (keys) and the
        names of the new, merged columns (values)
    The original columns that are merged are deleted from the 'count_table',
        while the new, merged columns are added to the table
    This allows characters with alternate spellings or names (e.g., 'Pig-Pen'
        and 'Pig Pen' to be reclassified under a single column
    Output:  'count_table' with the new, merged columns
    '''

    characters_merge = characters_merge_dict()
    i = 0       # ensures termination of loop in case of unanticipated error

    while i < count_table.shape[1]:

        col1_name, col2_name, new_name = find_two_columns_to_merge(
            count_table.columns, characters_merge)

        if not col1_name:
            break

        count_table = merge_two_columns(count_table, col1_name, col2_name,
                                        new_name)
        i += 1

    return(count_table)


def merge_characters_multiple_tables(counts):
    '''
    Loops function 'merge_character_counts_into_single_columns' for each
        count table in 'counts'
    Description of 'merge_character_counts_into_single_columns':
        Inputs:  'count_table' is a table/Pandas DataFrame that tallies whether a
            word or phrase (naming characters) appeared in items of text; each word
            has its own column; each row corresponds to an item of text; if a word
            appeared in a text item, the corresponding cell in the 'count_table'
            is '1', otherwise it's '0'
        Merges columns in 'count_table' as specified in the dictionary
            'characters_merge', which names the columns to be merged (keys) and the
            names of the new, merged columns (values)
        The original columns that are merged are deleted from the 'count_table',
            while the new, merged columns are added to the table
        This allows characters with alternate spellings or names (e.g., 'Pig-Pen'
            and 'Pig Pen' to be reclassified under a single column
    '''

    for i in range(len(counts)):
        counts[i] = merge_character_counts_into_single_columns(counts[i])

    return(counts)


def adjust_patty_counts_in_table(dates_column, count_table, pep_patty_dates):
    '''
    Adjusts counts for Patty and Peppermint Patty
    For 5 dates, Peppermint Patty is referred to only as 'Patty', so 'patty'
        counts are reassigned to 'peppermint patty' for these dates
    Peppermint Patty and Patty never appear in a comic together, so all 'patty'
        counts on Peppermint Patty appearance dates are set to '0', indicating
        that she didn't appear
    '''

    # 5 dates at end are when Peppermint Patty is referred to only as 'Patty'
    add_pep_dates = pep_patty_dates[-5:]

    # for these dates, assign 'patty' counts to 'peppermint patty'
    idx = dates_column[dates_column.isin(add_pep_dates)].index.values
    count_table.ix[idx, 'peppermint patty'] = count_table.ix[idx, 'patty']

    # for dates when Peppermint Patty appears, remove any appearances for 'Patty'
    # (they never appear in a comic together)
    idx = dates_column[dates_column.isin(pep_patty_dates)].index.values
    count_table.ix[idx, 'patty'] = 0

    return(count_table)


def adjust_patty_counts_multiple_tables(dates_column, counts, pep_patty_dates):
    '''
    Loops function 'adjust_patty_counts_in_table' for each
        count table in 'counts'
    Description of 'adjust_patty_counts_in_table':
        Adjusts counts for Patty and Peppermint Patty
        For 5 dates, Peppermint Patty is referred to only as 'Patty', so 'patty'
            counts are reassigned to 'peppermint patty' for these dates
        Peppermint Patty and Patty never appear in a comic together, so all 'patty'
            counts on Peppermint Patty appearance dates are set to '0', indicating
            that she didn't appear
    '''

    for i in range(len(counts)):
        counts[i] = adjust_patty_counts_in_table(dates_column, counts[i],
                                                 pep_patty_dates)

    return(counts)


def create_appearances_dict():
    '''
    Creates dictionary of first and last appearances (or mentions, sometimes)
        for several characters in the Peanuts comic strip
    '''

    dates = {'sally'                : ['1959-08-23', '2000-02-06'],
             'rerun'                : ['1973-03-26', '2000-01-30'],
             'woodstock'            : ['1966-03-04', '2000-01-16'],
             #'peppermint'          : ['1966-08-22', '2000-02-13'],
             'violet'               : ['1951-02-07', '1997-11-27'],
             'marcie'               : ['1971-07-20', '2000-01-02'],
             'spike'                : ['1975-08-13', '1999-12-21'],
             'franklin'             : ['1968-07-31', '1995-11-05'],
             'andy'                 : ['1994-02-14', '1999-09-27'],
             'olaf'                 : ['1989-01-16', '1999-09-27'],
             'frieda'               : ['1961-03-06', '1985-11-22'],
             'eudora'               : ['1978-06-13', '1987-06-13'],
             'truffles'             : ['1975-03-31', '1977-01-29'],
             'peggy jean'           : ['1990-07-23', '1999-07-11'],
             'pig pen'              : ['1954-07-13', '1999-09-08'],
             'othmar'               : ['1959-10-06', '1973-09-11'],
             'roy'                  : ['1965-06-11', '1984-05-27'],
             'cormac'               : ['1992-07-17', '2000-02-06'],     # don't know last appearance
             'thibault'             : ['1970-06-04', '1973-08-04'],
             'sophie'               : ['1968-06-18', '1987-08-19'],
             'poochie'              : ['1972-12-17', '1973-01-07'],
             'naomi'                : ['1998-10-01', '2000-02-06'],     # don't know last appearance
             'maynard'              : ['1986-07-21', '1986-07-30'],
             'lydia'                : ['1986-06-09', '1999-03-23'],
             'lila'                 : ['1968-02-17', '1968-08-31'],
             'larry'                : ['1991-05-28', '1991-12-19'],
             'royanne'              : ['1993-04-01', '1994-03-12'],
             'harold'               : ['1983-12-16', '1984-05-20'],
             'benny'                : ['1982-04-15', '1982-05-01'],
             'molly volley'         : ['1977-05-09', '1991-01-01'],     # last appearance in 1990
             'charlotte braun'      : ['1954-11-30', '1955-02-01'],
             'crybaby boobie'       : ['1978-07-03', '1997-03-10'],
             'tapioca pudding'      : ['1986-09-04', '1986-12-01'],
             'helen sweetstory'     : ['1971-04-09', '1972-11-30'],     # last mention Nov 1972
             'the school building'  : ['1974-08-31', '1979-12-31'],     # dies and rebuilt in 1976; unsure of last appearance
             'ethan'                : ['1993-07-14', '1993-07-15'],
             'floyd'                : ['1976-07-20', '1976-08-06'],
             'shirley'              : ['1968-06-18', '1987-07-20'],
             'emily'                : ['1995-02-11', '1999-12-31'],     # last appearance in 1999
             'belle'                : ['1976-06-22', '1981-05-11'],
             'faron'                : ['1961-05-23', '1961-11-20'],
             'harriet'              : ['1980-05-12', '2000-02-06'],     # don't know last appearance
             'bill'                 : ['1978-03-27', '2000-02-06'],     # don't know last appearance
             'conrad'               : ['1978-03-27', '2000-02-06'],     # don't know last appearance
             'olivier'              : ['1978-03-27', '2000-02-06'],     # don't know last appearance
             'raymond'              : ['1988-10-13', '2000-02-06'],     # don't know last appearance
             'fred'                 : ['1990-04-03', '1993-05-13'],
             'wilson'               : ['1984-12-02', '1998-06-06']}

    return(dates)


def adjust_counts_by_appearance_dates_in_table(dates_column, count_table):
    '''
    Adjusts counts so that characters can't appear before their debut dates or
        after their final dates in the comic strip
    Characters might erroneously appear outside their appearance dates because
        of typoes or non-specific uses of their names (e.g., 'sally', 'rerun',
        'violet', and 'spike' have meanings beyond the characters' names
    '''

    dates = create_appearances_dict()
    column_names = count_table.columns

    for i in range(len(column_names)):

        if column_names[i] in dates:
            start_end_dates = dates[column_names[i]]
            start_idx = min(dates_column[dates_column ==
                                         start_end_dates[0]].index.values)
            end_idx = max(dates_column[dates_column ==
                                       start_end_dates[1]].index.values)
            count_table.iloc[:start_idx, i] = 0
            count_table.iloc[end_idx+1:, i] = 0

    return(count_table)


def adjust_counts_by_appearance_dates_multiple_tables(dates_column, counts):
    '''
    Loops function 'adjust_counts_in_table_by_appearance_dates' for each
        count table in 'counts'
    Description of 'adjust_counts_in_table_by_appearance_dates':
        Adjusts counts so that characters can't appear before their debut dates or
            after their final dates in the comic strip
        Characters might erroneously appear outside their appearance dates because
            of typoes or non-specific uses of their names (e.g., 'sally', 'rerun',
            'violet', and 'spike' have meanings beyond the characters' names
    '''

    for i in range(len(counts)):
        counts[i] = adjust_counts_by_appearance_dates_in_table(dates_column,
                                                               counts[i])

    return(counts)


def correct_misidentified_characters_in_table(dates_column, count_table,
                                              misidentifications):
    '''
    Switches characters' counts on dates when a character was misidentified
    'dates_column' - Pandas Data Series with dates/filenames
    'count_table' - Pandas DataFrame/table that tallies whether a word or phrase
        (naming characters) appeared in items of text; each word has its own
        column; each row corresponds to an item of text; if a word appeared in a
        text item, the corresponding cell in the 'count_table' is '1', otherwise
        it's '0'
    'misidentifications' - list of lists, each of which contains 3 items:
        the date/filename of the comic in which a character was misidentified,
        the incorrect character that appears in the text description of the
        comic, and the correct character who actually appears in the comic
    Returns corrected 'count_table'
    '''
    for i in range(len(misidentifications)):

        idx = dates_column[dates_column == misidentifications[i][0]].index.values
        temp = count_table.ix[idx, misidentifications[i][2]]
        count_table.ix[idx, misidentifications[i][2]] = count_table.ix[idx,
                                                        misidentifications[i][1]]
        count_table.ix[idx, misidentifications[i][1]] = temp

    return(count_table)


def correct_misidentified_characters_multiple_tables(dates_column, counts,
                                                     misidentifications):
    '''
    Loops function 'correct_misidentified_characters_in_table' for each
        count table in 'counts'
    Description of 'correct_misidentified_characters_in_table':
        Switches characters' counts on dates when a character was misidentified
        'dates_column' - Pandas Data Series with dates/filenames
        'count_table' - Pandas DataFrame/table that tallies whether a word or phrase
            (naming characters) appeared in items of text; each word has its own
            column; each row corresponds to an item of text; if a word appeared in a
            text item, the corresponding cell in the 'count_table' is '1', otherwise
            it's '0'
        'misidentifications' - list of lists, each of which contains 3 items:
            the date/filename of the comic in which a character was misidentified,
            the incorrect character that appears in the text description of the
            comic, and the correct character who actually appears in the comic
        Returns corrected 'count_table'
    '''

    for i in range(len(counts)):
        counts[i] = correct_misidentified_characters_in_table(dates_column,
                                                counts[i], misidentifications)

    return(counts)


def snoopy_and_personas_in_table(count_table):
    '''
    Adds column to 'count_table' that counts Snoopy and his personas, in case
        some text descriptions refer to him by the persona and not by 'Snoopy',
        which would undercount Snoopy's appearances
    '''

    count_table['snoopy and personas'] = (count_table['snoopy'] |
                                          count_table['world famous'] |
                                          count_table['joe cool'] |
                                          count_table['joe motocross'] |
                                          count_table['joe blackjack'] |
                                          count_table['joe sandbagger'] |
                                          count_table['joe grunge'] |
                                          count_table['flying ace'] |
                                          count_table['literary ace'] |
                                          count_table['masked marvel'] |
                                          count_table['easter beagle'] |
                                          count_table['lone beagle'] |
                                          count_table['revolutionary war patriot'] |
                                          count_table['legionnaire'])

    return(count_table)


def snoopy_and_personas_multiple_tables(counts):
    '''
    Loops function 'snoopy_and_personas_in_table' for each
        count table in 'counts'
    Description of 'snoopy_and_personas_in_table':
        Adds column to 'count_table' that counts Snoopy and his personas, in case
            some text descriptions refer to him by the persona and not by 'Snoopy',
            which would undercount Snoopy's appearances
    '''

    for i in range(len(counts)):
        counts[i] = snoopy_and_personas_in_table(counts[i])

    return(counts)


def save_tables_to_csv(list_of_tables, list_of_filenames):
    '''
    Saves Pandas DataFrames/tables in a list to 'csv' files
    '''

    for i in range(len(list_of_tables)):
        list_of_tables[i].to_csv(list_of_filenames[i] + '.csv',
                                 sep=',', index=True)


def counts_by_comic_multiple_tables(dates_column, num_panels_column,
                                    panels_with_characters, counts):
    '''
    Groups panels by comic strip date, so that each row represents a comic (with
        1 or more panels) instead of a panel
    'dates_column' - Pandas Data Series with dates/filenames
    'num_panels_column' - Pandas Data Series with number of panels in that comic
    'count_table' - Pandas DataFrame/table that tallies whether a word or phrase
        (naming characters) appeared in items of text (each item corresponds to
        a panel); each word has its own column; each row corresponds to an item
        of text; if a word appeared in a text item, the corresponding cell in
        the 'count_table' is '1', otherwise it's '0'
    'panel_counts_by_comic' - counts are summed over panels per comic, i.e., in
        how many panels did this character appear in the comic?
    'counts_by_comic' - panel counts per comic are transformed into Boolean; did
        the character appear in this comic, yes or no?
    'proportions_by_comic' - summed counts per comic are divided by the number
        of panels in that comic
    'props_w_chars_by_comic' - summed counts per comic are divided by the number
        of panels that include a mention of a character in that comic; e.g., if
        the text description of a 4-panel comic mentions 'Snoopy' only once in
        the 1st panel and thereafter refers to him as 'he', then
        'proportions_by_comic' counts Snoopy's proportion as 1 / 4 = 0.25,
        whereas 'props_w_chars_by_comic' counts Snoopy at 1 / 1 = 1
    '''

    num_panels_by_comic = num_panels_column.groupby(dates_column).median()
    num_panels_w_chars_by_comic = panels_with_characters.groupby(dates_column).sum()
    panel_counts_by_comic = []
    counts_by_comic = []
    proportions_by_comic = []
    props_w_chars_by_comic = []

    for i in range(len(counts)):
        panel_counts_by_comic.append(counts[i].groupby(dates_column).sum())
        counts_by_comic.append(panel_counts_by_comic[i] > 0)
        proportions_by_comic.append(panel_counts_by_comic[i].divide(
            num_panels_by_comic, axis='index'))
        props_w_chars_by_comic.append(panel_counts_by_comic[i].divide(
            num_panels_w_chars_by_comic, axis='index'))

    return(panel_counts_by_comic, counts_by_comic, proportions_by_comic,
           props_w_chars_by_comic)


def main():
    '''
    Searches for words or phrases (mostly character names) in text descriptions
        of Peanuts and marks whether each word or phrase appears in each
        text description
    Adjusts counts in several ways:
        1) combines word/phrases that refer to the same character (e.g.,
            'Pig-Pen' and 'Pig Pen')
        2) corrects counts to distinguish between Patty and Peppermint Patty
        3) removes any appearances that occur before a character's first
            appearance in the comic strip or after the character's last
            appearance
        4) corrects for some cases where characters are misidentified by the
            text description of the comic (based only on happenstance
            observations, not on a systematic or comprehensive search for such
            misidentifications)
        5) provides combined count data for Snoopy and many of his personas, in
            case Snoopy is sometimes referred to by only a persona in a text
            description of a comic
    Provides count data for each panel (Boolean:  whether the word/phrase
        appears or not) in a comic and for each comic (sum of appearances for
        panels of that comic); also provides per-comic data as proportions
        (i.e., in what proportion of panels did the word/phrase appear for that
        comic?)
    Also provides summary tables of per-panel and per-comic count data
    '''

    import os

    table_folder = '07_separate_talk'
    table_file = 'expanded_table.csv'
    source_path = get_sibling_directory_path(table_folder)
    table_filepath = os.path.join(source_path, table_file)

    text_col_names = ['comics_speakers', 'text_nontalk', 'text_talk']
    expanded_table = read_table(table_filepath, text_col_names)
    expanded_table.to_csv('expanded_table.csv', sep='^', index=False)
    dates_column = expanded_table.ix[:, 'filename']         # convenient for later use

    # reading 'expanded_table' from the 'csv' file produces 11 NaN values in
    # each of the columns 'text_by_panels' and 'text_spell_corrected'; manual
    # inspection of each case showed that no text was being lost; deleting the
    # rows may disrupt some subsequent loops, and the NaNs won't affect the
    # character counts
    nan_n = expanded_table.ix[:, 'text_by_panels'].isnull().sum()
    panels_n = len(expanded_table) - nan_n
    #expanded_table.ix[:, 'text_by_panels'].fillna('', inplace=True)
    expanded_table.ix[:, 'text_spell_corrected'].fillna('', inplace=True)

    # names of characters to be counted
    # NOTE:  any non_character words included in the 'character_file' could
    # adversely affect the proportions in 'props_w_chars_by_comic'
    # 'characters_only.txt' includes characters only and is used for calculating
    # proportions in 'props_w_chars_by_comic'
    character_file = 'characters_only.txt'
    characters_only = read_text_file(character_file)
    character_file = 'characters_and_more.txt'
    characters = read_text_file(character_file)
    characters = [s.lower() for s in characters]
    characters = add_possessives_to_word_list(characters)   # tokenizer includes possessives

    # count the characters' appearances/mentions
    counts = count_characters(expanded_table, characters)
    counts_summary_1 = counts_summary_table(counts)
    counts_summary_1.to_csv('counts_summary_01.csv', sep=',', index=True)

    # merge counts for multiple search terms into single column with single name
    # e.g., counts for 'Pig-Pen' and 'Pig Pen' are merged together under 'Pig-Pen'
    counts = merge_characters_multiple_tables(counts)
    counts_summary_2 = counts_summary_table(counts)
    counts_summary_2.to_csv('counts_summary_02.csv', sep=',', index=True)

    # correct counts to distinguish between Patty and Peppermint Patty
    patty_folder = '06_character_talk'
    patty_file = 'peppermint_patty_dates.txt'
    patty_path = get_sibling_directory_path(patty_folder)
    patty_filepath = os.path.join(patty_path, patty_file)
    pep_patty_dates = read_text_file(patty_filepath)
    write_list_to_text_file(pep_patty_dates, patty_file, 'w')

    counts = adjust_patty_counts_multiple_tables(dates_column, counts,
                                                 pep_patty_dates)
    counts_summary_3 = counts_summary_table(counts)
    counts_summary_3.to_csv('counts_summary_03.csv', sep=',', index=True)

    # remove appearances/mentions that occur outside a character's appearance dates
    counts = adjust_counts_by_appearance_dates_multiple_tables(dates_column,
                                                               counts)
    counts_summary_4 = counts_summary_table(counts)
    counts_summary_4.to_csv('counts_summary_04.csv', sep=',', index=True)
    counts_summary_5 = counts_summary_3 - counts_summary_4
    counts_summary_5.to_csv('counts_summary_05.csv', sep=',', index=True)

    # characters misidentified in text descriptions:  date, incorrect character,
    # correct character
    misidentifications = [['1999-09-19', 'linus', 'rerun'],
                          ['1999-11-23', 'linus', 'rerun'],
                          ['1999-12-05', 'rerun', 'linus']]
    # correct counts for misidentified characters
    counts = correct_misidentified_characters_multiple_tables(dates_column,
                                                    counts, misidentifications)
    counts_summary_6 = counts_summary_table(counts)
    counts_summary_6.to_csv('counts_summary_06.csv', sep=',', index=True)

    # some text descriptions might refer to Snoopy only by one of his personas,
    # which would produce and undercount of Snoopy's appearances under 'snoopy';
    # so, add a new column that includes appearances/mentions of Snoopy and
    # his major personas combined
    counts = snoopy_and_personas_multiple_tables(counts)
    counts_summary_7 = counts_summary_table(counts)
    counts_summary_7.to_csv('counts_summary_07.csv', sep=',', index=True)

    # calculate counts per comic, instead of per panel
    num_panels_column = expanded_table.ix[:, 'num_panels']
    panels_with_characters = counts[0][characters_only].any(axis=1)
    (panel_counts_by_comic, counts_by_comic,
     proportions_by_comic, props_w_chars_by_comic) = (
         counts_by_comic_multiple_tables(dates_column, num_panels_column,
                                         panels_with_characters, counts))
    panel_counts_by_comic_summary = counts_summary_table(panel_counts_by_comic)
    #panel_counts_by_comic_summary.to_csv('panel_counts_by_comic_summary.csv',
    #                                     sep=',', index=True)
    counts_by_comic_summary = counts_summary_table(counts_by_comic)
    counts_by_comic_summary.to_csv('counts_by_comic_summary.csv',
                                   sep=',', index=True)

    # save counts tables
    count_types = ['1_overall', '2_nontalk', '3_talk',
                   '4_odd_quotes', '5_no_quotes']
    counts_filenames = ['counts_by_panel_' + e for e in count_types]
    counts_by_comic_filenames = ['counts_by_comic_' + e for e in count_types]
    proportions_by_comic_filenames = ['proportions_by_comic_' + e
                                      for e in count_types]
    props_w_chars_by_comic_filenames = ['proportions_with_chars_by_comic_' + e
                                        for e in count_types]

    save_tables_to_csv(counts, counts_filenames)
    save_tables_to_csv(counts_by_comic, counts_by_comic_filenames)
    #save_tables_to_csv(proportions_by_comic, proportions_by_comic_filenames)
    save_tables_to_csv(props_w_chars_by_comic, props_w_chars_by_comic_filenames)


if __name__ == '__main__':
    main()
