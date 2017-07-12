#!/usr/bin/env python
"""Format LaTeX source code"""
# Copyright (C) 2017 Michael Goerz. See LICENSE for terms of use.
import logging
import fileinput
import textwrap
import re
import sys

import click

RX_LATEX_COMMAND = re.compile(r'\s*\\')
RX_LATEX_SECTION = re.compile(
    r'\s*\\(part|chapter|section|subsection|subsubsection|image)')
# RX_LATEX_COMMENT  = re.compile(r'\s*%')
RX_LATEX_COMMENT = re.compile(
    # matching either "   %" or anything different than
    # "\%" i.e. "sldjfksdfsfsldfkj%?dskfjskf"
    r'(.*[^\\]|\s*)%.*')
RX_LATEX_BEGIN = re.compile(r'\\begin')
RX_LATEX_BEGIN_DOC = re.compile(r'\\begin\{(document|abstract)')
RX_LATEX_END = re.compile(r'\\end')
RX_LATEX_END_DOC = re.compile(r'\\end\{(document|abstract)')
RX_EMPTY_LINE = re.compile(r'\s*$')
RX_FULL_STOP = re.compile(
    # sentence ending period only
    r'(?<=([\@$}0-9a-z]))\.(?![\\~])')


def split_first_sentence(line):
    try:
        m = next(RX_FULL_STOP.finditer(line))
    except StopIteration:
        return line, ''
    else:
        pos = m.span()[1]
        return line[:pos], line[pos:].lstrip()


def ends_with_full_stop(line):
    if RX_FULL_STOP.search(line.rstrip()[-2:]):
        return True
    else:
        return False


def process_line(
        cat_line, line, open_groups, stop_cat, reformat):
    """Process a single line"""
    logger = logging.getLogger(__name__)
    logger.debug("process_line: %s", line)
    l = line.strip()
    line_group_tally = 0
    break_and_protect = (
        RX_LATEX_COMMENT.match(l) or RX_LATEX_SECTION.match(l) or
        RX_LATEX_BEGIN_DOC.match(l) or RX_LATEX_END_DOC.match(l))
    # TODO: generalize break_and_protect into function
    # TODO: recognize more things that should stay on their own line, e.g.
    # command definitions
    in_group = False
    if not break_and_protect:
        n_begin = len(RX_LATEX_BEGIN.findall(l))
        n_end = len(RX_LATEX_END.findall(l))
        line_group_tally = n_begin - n_end
        if line_group_tally == 0 and open_groups == 0:
            first_sentence, rest = split_first_sentence(l)
            if len(cat_line) > 0:
                cat_line += " %s" % first_sentence
            else:
                cat_line = first_sentence
            line = rest
            if (len(rest) > 0) or ends_with_full_stop(first_sentence):
                stop_cat = True
        else:
            in_group = True
    if break_and_protect or in_group:
        if len(cat_line) == 0:
            cat_line = line.rstrip()
            line, reformat, stop_cat = '', False, True
            open_groups += line_group_tally
        else:
            # return the existing cat_line, leave line for next call
            stop_cat = True
    logger.debug(
        ("  -> cat_line '%s', line '%s', open_groups %s, stop_cat %s, "
         "reformat %s"), cat_line, line, open_groups, stop_cat, reformat)
    return cat_line, line, open_groups, stop_cat, reformat


def reformat_cat_line(cat_line, width, open_groups, reformat):
    if open_groups == 0 and reformat:
        dedented_text = textwrap.dedent(cat_line.strip())
        wrapped_text = textwrap.fill(
            dedented_text, width=width, break_on_hyphens=False,
            break_long_words=False)
        return wrapped_text
    else:
        return cat_line


def format_latex(lines, width=80):
    """Re-format lines of Latex text

    Args:
        lines (iterable): An iterable of lines
        width (int): width at which to wrap
    """
    logger = logging.getLogger(__name__)
    out_buffer = []
    open_groups = 0
    cat_line = ''  # accumulated line
    stop_cat = False
    reformat = True
    new_par = True
    for line in lines:
        assert line.endswith("\n")
        if len(line.strip()) == 0:
            logger.debug("Read blank line")
            new_par = True
            if len(cat_line) > 0:
                out_text = reformat_cat_line(
                    cat_line, width, open_groups, reformat)
                logger.debug("Adding to out_buffer: %s", repr(out_text))
                out_buffer.append(out_text)
            logger.debug("Adding to out_buffer: '' (paragraph end)")
            out_buffer.append("")
            cat_line, stop_cat, reformat = '', False, True
        else:
            # TODO: determine indent if new_par
            new_par = False
            while len(line) > 0:
                cat_line, line, open_groups, stop_cat, reformat = process_line(
                    cat_line, line, open_groups, stop_cat, reformat)
                if stop_cat:
                    out_text = reformat_cat_line(
                        cat_line, width, open_groups, reformat)
                    logger.debug("Adding to out_buffer: %s", repr(out_text))
                    out_buffer.append(out_text)
                    cat_line, stop_cat, reformat = '', False, True
    if len(cat_line) > 0:
        out_text = reformat_cat_line(cat_line, width, open_groups, reformat)
        logger.debug("Adding to out_buffer: %s", repr(out_text))
        out_buffer.append(out_text)
    return "\n".join(out_buffer)


@click.command()
@click.help_option('--help', '-h')
@click.option(
    '--debug', is_flag=True, help='enable debug logging')
@click.argument('input', type=click.File('r'), default='-')
@click.argument('output', type=click.File('w'), default='-')
def main(debug, input, output):
    """Format LaTeX source code

    Read from INFILE and write to OUTFILE. If INFILE and/or OUTFILE are omitted
    or are '-', read/write from/to stdin/stdout.
    """
    # TODO: standalone or snippet option that ignores header
    logging.basicConfig(level=logging.WARNING)
    logger = logging.getLogger(__name__)
    if debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Enabled debug output")
    sys.stdout.write(format_latex(fileinput.input()))


if __name__ == "__main__":
    main()
