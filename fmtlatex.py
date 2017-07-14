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
RX_LATEX_COMMENT = re.compile(
    r'(.*[^\\]|\s*)%.*')
RX_LATEX_BEGIN = re.compile(r'\\begin')
RX_LATEX_BEGIN_DOC = re.compile(r'\\begin\{(document|abstract)')
RX_LATEX_END = re.compile(r'\\end')
RX_LATEX_END_DOC = re.compile(r'\\end\{(document|abstract)')
RX_EMPTY_LINE = re.compile(r'\s*$')
RX_FULL_STOP = re.compile(
    # sentence ending period only
    r'(?<=([\@$}\'0-9a-z]))\.(?![,\w\\~])')


def split_first_sentence(line):
    """Split the line at the first full stop. If there is no full stop, return
    tupel (line, '')"""
    try:
        m = next(RX_FULL_STOP.finditer(line))
    except StopIteration:
        return line, ''
    else:
        pos = m.span()[1]
        return line[:pos], line[pos:].lstrip()


def ends_with_full_stop(line):
    """Check whether the given `line` ends with full stop (ignoring
    whitespace)"""
    if RX_FULL_STOP.search(line.rstrip()[-2:]):
        return True
    else:
        return False


def is_protected(line):
    """Check whether the given line is "protected". Protected lines must stay
    isolated, they are not concatenated with previous or following lines"""
    # TODO: recognize more things that should stay on their own line, e.g.
    # command definitions
    rxs = [RX_LATEX_COMMENT, RX_LATEX_SECTION, RX_LATEX_BEGIN_DOC,
           RX_LATEX_END_DOC]
    for rx in rxs:
        if rx.match(line):
            return True
    return False


def group_tally(line):
    r"""Return a tally on how the given line affects  the number of open groups
    (things between \begin{...} and \end{...}).

    A positive number indicates that the line opens groups, and a negative
    number indicates that it closes groups.
    """
    n_begin = len(RX_LATEX_BEGIN.findall(line))
    n_end = len(RX_LATEX_END.findall(line))
    return n_begin - n_end


def process_line(cat_buffer, line, open_groups):
    r"""Process a single line of LaTeX text

    Args:
        cat_buffer (str)
        line (str)
        open_groups(int)

    Returns:
        A tuple `cat_buffer`, `line`, `open_groups`, `ready_for_output`,
        `protect`, with values as follows:

        * `cat_buffer` is the input `cat_buffer`, possibly extended with data
          from the input `line`
        * `line` is the remainder of the input `line` that is left unprocessed
          If non-emtpy, the output `line` should be passed to another
          invocation of :func:`process_line`
        * `open_groups` is the updated number of open groups (things between
          \begin{...} and \end{...}). That is, the input `open_groups` adjusted
          by the groups opened/closed in the input `line`
        * `ready_for_output` is a value that indicates that the output
          `cat_buffer` is ready to be put out
        * `protect` indicates that (assuming `ready_for_output`), the output
          `cat_buffer` should be written without reflowing
    """
    logger = logging.getLogger(__name__)
    logger.debug("process_line: %s", line)
    l = line.strip()
    line_group_tally = 0
    ready_for_output = False
    protect = is_protected(l)
    in_group = False
    if not protect:
        line_group_tally = group_tally(l)
        if line_group_tally == 0 and open_groups == 0:
            first_sentence, rest = split_first_sentence(l)
            if len(cat_buffer) > 0:
                cat_buffer += " %s" % first_sentence
            else:
                cat_buffer = first_sentence
            line = rest
            if (len(rest) > 0) or ends_with_full_stop(first_sentence):
                ready_for_output = True
        else:
            in_group = True
    if in_group:
        protect = True
    if protect:
        if len(cat_buffer) == 0:
            cat_buffer = line.rstrip()
            line, ready_for_output = '', True
            open_groups += line_group_tally
        else:
            # leave line for next call
            ready_for_output = True
            protect = False
    logger.debug(
        ("  -> cat_buffer '%s', line '%s', open_groups %s, "
         "ready_for_output %s, protect %s"), cat_buffer, line, open_groups,
        ready_for_output, protect)
    return cat_buffer, line, open_groups, ready_for_output, protect


def reflow(text, width, protect):
    """Reflow the given `text` with line width `width`

    Return unchanged `text` if `protect` is True.
    """
    if protect:
        return text
    else:
        dedented_text = textwrap.dedent(text.strip())
        wrapped_text = textwrap.fill(
            dedented_text, width=width, break_on_hyphens=False,
            break_long_words=False)
        return wrapped_text


def format_latex(lines, width=80):
    """Re-format lines of Latex text

    Args:
        lines (iterable): An iterable of lines
        width (int): width at which to wrap
    """
    logger = logging.getLogger(__name__)
    out_buffer = []
    open_groups = 0
    cat_buffer = ''  # accumulated line
    protect = False
    new_par = True
    for line in lines:
        assert line.endswith("\n")
        if len(line.strip()) == 0:
            logger.debug("Read blank line")
            new_par = True
            if len(cat_buffer) > 0:
                out_text = reflow(cat_buffer, width, protect)
                logger.debug("Adding to out_buffer: %s", repr(out_text))
                out_buffer.append(out_text)
            logger.debug("Adding to out_buffer: '' (paragraph end)")
            out_buffer.append("")
            cat_buffer, protect = '', False
        else:
            # TODO: determine indent if new_par
            new_par = False
            while len(line) > 0:
                cat_buffer, line, open_groups, ready_for_output, protect \
                    = process_line(cat_buffer, line, open_groups)
                if ready_for_output:
                    out_text = reflow(cat_buffer, width, protect)
                    logger.debug("Adding to out_buffer: %s", repr(out_text))
                    out_buffer.append(out_text)
                    cat_buffer, protect = '', False
    if len(cat_buffer) > 0:
        out_text = reflow(cat_buffer, width, protect)
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
