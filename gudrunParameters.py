"""gudrunParameters.py - code to read in parameters from purge_det.dat and gudrun_dcs.dat files

Copyright (C) 2013 Christopher Kerr
This file is free software, you may use it under the terms of the GNU General
Public License (GPL) version 3 or, at your option, any later version.
"""

__all__ = ['PurgeDetParameterSet', 'GudrunParameterSet']


import re
import os.path


def parseParameterSection(text):
    """Parse a section of a gudrun_dcs.dat or purge_det.dat file"""
    
    if isinstance(text, str):
        lines = re.split(r'\r?\n', text)
    else:
        lines = list(text)
    
    parsed_lines = []
    line_dict = {}
    for i, line in enumerate(lines):
        match = re.match(r'(\S(?:.*?\S)??)(?: {10}(\S(?:.*\S)?))?\s*$', line)
        if match:
            data, comment = match.groups(default=None)
            #data = tuple(data.split())
            parsed_lines.append((data, comment))
            if comment is None:
                line_dict[i] = data
            elif comment == '{':
                raise SyntaxError("Found a { - is this a Gudrun_DCS section?\n" + line)
            else:
                line_dict[comment] = data
        elif (i + 1) == len(lines) and re.match('\s*$', line):
            continue  # Ignore blank lines at end of section
        else:
            raise SyntaxError("Line does not match:\n" + line)
    
    return parsed_lines, line_dict


def parsed_lines_eq(lines1, lines2):
    if len(lines1) != len(lines2):
        return False
    
    for line1, line2 in zip(lines1, lines2):
        if line1[0] != line2[0]:  # only check if data are equal
            return False
    
    return True


def parsed_lines_get_param(lines, line_no, comment_re):
    data, comment = lines[line_no]
    if comment is not None and comment_re is not None:
        if not re.match(comment_re, comment):
            raise KeyError("comment '%s' does not match re '%s'" % (comment, comment_re))
    return data

class PurgeDetParameterSet(object):
    
    def __init__(self, initialiser):
        if os.path.exists(initialiser):
            with open(initialiser, 'r') as fid:
                self.text = fid.read()
            self.source_file = initialiser
        else:
            self.text = str(initialiser)
            
        self.lines = re.split(r'\r?\n', self.text)
        if self.lines[0] != "'  '  '          '  '/'":
            raise SyntaxError("Wrong first line for purge_det file\n" + self.lines[0])
        if self.lines[1] != '':
            raise SyntaxError("Wrong second line for purge_det file\n" + self.lines[1])
            
        self.parsed_lines, self.line_dict = parseParameterSection(self.lines[2:])
    
    def __getitem__(self, name):
        if name in self.line_dict:
            return self.line_dict[name]
        else:
            raise AttributeError
    
    def __eq__(self, other):
        if not isinstance(other, PurgeDetParameterSet):
            return False
        return parsed_lines_eq(self.parsed_lines, other.parsed_lines)
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def as_dict(self):
        return self.line_dict
    
    def save(self, filename, add_extension=False):
        """Do nothing
        
        The way Sumatra handles parameter sets does not fit the way
        Gudrun works. The simplest option is to do nothing here.
        """
        return ''
        #if add_extension:
            #filename += '-purge_det.dat'
        #with open(filename, 'w') as fid:
            #fid.write(self.pretty())
        #return filename
        
            
    def pop(self, k, d=None):
        return self.line_dict.pop(k, d)
    
    def update(self, E, **F):
        return self.line_dict.update(E, **F)
    
    def pretty(self, expand_urls=False):
        text = "'  '  '          '  '/'\n\n"
        for data, comment in self.parsed_lines:
            #text += (' '.join(data))
            text += data
            if comment is None:
                text += '\n'
            else:
                text += ('          %s\n' % comment)
        text += '\n'
        return text
    
    def get_param(self, line, comment_re = None):
        return parsed_lines_get_param(self.parsed_lines, line, comment_re)


class GudrunParameterSet(object):
    
    def __init__(self, initialiser, truncate_after_end=False):
        if os.path.exists(initialiser):
            with open(initialiser, 'r') as fid:
                self.text = fid.read()
            self.source_file = initialiser
        else:
            self.text = str(initialiser)
        
        unmatched_text = self.text
        
        match = re.match(r"'  '  '          '  '/'\r?\n\r?\n", unmatched_text)
        if match is None:
            raise SyntaxError("Invalid start for gudrun_dcs.dat file: " + line)
        
        self.sections_or_go = []
        self.section_dict = {}
        while True:
            unmatched_text = unmatched_text[match.end():]
            
            match = re.match(r'(\S(?:.*?\S)?) {10}\{\n\n([^{}]+?)\n\n\}\n\n', unmatched_text)
            if match:
                section_name = match.group(1)
                parsed_lines, line_dict = parseParameterSection(match.group(2))
                self.sections_or_go.append((section_name, parsed_lines, line_dict))
                self.section_dict[section_name] = line_dict
                continue
            
            match = re.match(r'GO *\n\n', unmatched_text)
            if match:
                self.sections_or_go.append(('GO', None, None))
                continue
            
            match = re.match(r'(\s*\n)?END\s*\n', unmatched_text)
            if match:
                self.end = (len(self.text) - len(unmatched_text)) + match.end()
                break
            
            raise SyntaxError("Could not parse remainder of gudrun_dcs.dat file\n" + unmatched_text)
    
    def __getitem__(self, name):
        if name in self.section_dict:
            return self.section_dict[name]
        else:
            raise AttributeError
    
    def __eq__(self, other):
        if not isinstance(other, GudrunParameterSet):
            return False
        
        if len(self.sections_or_go) != len(other.sections_or_go):
            return False
        
        for my_section, other_section in zip(self.sections_or_go, other.sections_or_go):
            my_name, my_parsed_lines, my_line_dict = my_section
            other_name, other_parsed_lines, other_line_dict = other_section
            
            if my_name != other_name:
                return False
            
            if my_name == 'GO':
                continue
            else:
                if not parsed_lines_eq(my_parsed_lines, other_parsed_lines):
                    return False
                
        return True
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def as_dict(self):
        return self.section_dict
    
    def save(self, filename, add_extension=False):
        """Do nothing
        
        The way Sumatra handles parameter sets does not fit the way
        Gudrun works. The simplest option is to do nothing here.
        """
        return ''
        #if add_extension:
            #filename += '-gudrun_dcs.dat'
        #with open(filename, 'w') as fid:
            #fid.write(self.pretty())
        #return filename
            
    def pop(self, k, d=None):
        return self.section_dict.pop(k, d)
    
    def update(self, E, **F):
        return self.section_dict.update(E, **F)
    
    def pretty(self, expand_urls=False):
        text = "'  '  '          '  '/'\n\n"
        for name, parsed_lines, line_dict in self.sections_or_go:
            text += name
            if parsed_lines is None:
                text += '\n\n'
            else:
                text += '          {\n\n'
                for data, comment in parsed_lines:
                    #text += (' '.join(data))
                    text += data
                    if comment is None:
                        text += '\n'
                    else:
                        text += ('          %s\n' % comment)
                text += '\n}\n\n'
        text += '\nEND\n'
        return text
    
    def get_param(self, section_no, line_no, section_re=None, comment_re = None):
        section_name, parsed_lines, line_dict = self.sections_or_go[section_no]
        if section_re is not None:
            if not re.match(section_re, section_name):
                raise KeyError("section '%s' does not match re '%s'" % (section_name, section_re))

        return parsed_lines_get_param(parsed_lines, line_no, comment_re)

    def get_data_files(self):
        data_files = []
        for section_name, parsed_lines, line_dict in self.sections_or_go:
            if re.match('NORMALISATION|SAMPLE .+|CONTAINER .+', section_name):
                numbers = parsed_lines_get_param(parsed_lines, 0,
                                                 'Number of  files and period number')
                nfiles, period_no = map(int, numbers.split())
                for i in range(1, nfiles + 1):
                    data_files.append(parsed_lines_get_param(parsed_lines, i,
                                                             '.*[Dd]ata files'))
                if section_name == 'NORMALISATION':
                    second_match_start = nfiles + 1
                    numbers = parsed_lines_get_param(parsed_lines, second_match_start,
                                                    'Number of  files and period number')
                    nfiles, period_no = map(int, numbers.split())
                    for i in range(second_match_start + 1, second_match_start + nfiles + 1):
                        data_files.append(parsed_lines_get_param(parsed_lines, i,
                                                                 '.*[Dd]ata files'))
        return data_files
                
                
