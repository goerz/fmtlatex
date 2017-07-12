"""Collection of tests for fmtlatex.py"""
from click.testing import CliRunner
from fmtlatex import format_latex, main
from textwrap import dedent
import pytest


def test_help():
    """Ensure that -h and --help display the help"""
    runner = CliRunner()
    result = runner.invoke(main, args=['-h'])
    result2 = runner.invoke(main, args=['--help'])
    assert result.exit_code == 0
    assert result.output.startswith("Usage:")
    assert result.output == result2.output


def to_lines(multiline_str):
    for line in multiline_str.split("\n"):
        yield line + "\n"


def test_simple():
    text_in = dedent(r'''
    In this paper, we consider a
    network consisting of a cascade
    of cavities. The network is depicted
    in \Fig{network}.
    ''').strip()
    expected = (
        'In this paper, we consider a network consisting of a cascade of '
        'cavities.\nThe network is depicted in \\Fig{network}.')
    result = format_latex(to_lines(text_in))
    assert result == expected
    assert(format_latex(to_lines(result))) == expected


def test_long():
    text_in = (
        'In this paper, we consider a network consisting of a cascade of '
        'cavities. The network is depicted in \Fig{network}.  For a single '
        'node labeled $(i)$, the Hamiltonian consists of drift term '
        '$\Op{H}_0$, a static qubit-cavity interaction $\Op{H}_{\interact}$, '
        'and a driving Jaynes-Cummings term $\Op{H}_{d}$.')
    expected = (
        'In this paper, we consider a network consisting of a cascade of '
        'cavities.\nThe network is depicted in \\Fig{network}.\nFor a single '
        'node labeled $(i)$, the Hamiltonian consists of drift '
        'term\n$\\Op{H}_0$, a static qubit-cavity interaction '
        '$\\Op{H}_{\\interact}$, and a\ndriving Jaynes-Cummings term '
        '$\\Op{H}_{d}$.')
    result = format_latex(to_lines(text_in))
    assert result == expected
    assert(format_latex(to_lines(result))) == expected


def test_long_comment():
    text_in = (
        'In this paper, we consider a network consisting of a cascade of\n'
        'cavities.\nThe network is depicted in \Fig{network}.  %For a single '
        'node labeled $(i)$, the Hamiltonian consists of drift term '
        '$\Op{H}_0$, a static qubit-cavity interaction $\Op{H}_{\interact}$, '
        'and a driving Jaynes-Cummings term $\Op{H}_{d}$.')
    expected = (
        'In this paper, we consider a network consisting of a cascade of '
        'cavities.\nThe network is depicted in \\Fig{network}.  %For a single '
        'node labeled $(i)$, the Hamiltonian consists of drift term '
        '$\\Op{H}_0$, a static qubit-cavity interaction '
        '$\\Op{H}_{\\interact}$, and a driving Jaynes-Cummings term '
        '$\\Op{H}_{d}$.')
    result = format_latex(to_lines(text_in))
    assert result == expected
    assert(format_latex(to_lines(result))) == expected


def test_short_comment():
    text_in = dedent(r'''
    For a single node labeled $(i)$, the
    Hamiltonian consists of drift term
    $\Op{H}_0$,
    a static qubit-cavity interaction $\Op{H}_{\interact}$, and a
    driving %Jaynes-Cummings term $\Op{H}_{d}$.
    term.
    In this paper, we consider a
    network consisting of a series %cascade
    of cavities. The network is depicted
    in \Fig{network}.
    ''').strip()
    expected = (
        'For a single node labeled $(i)$, the Hamiltonian consists of drift '
        'term\n$\\Op{H}_0$, a static qubit-cavity interaction '
        '$\\Op{H}_{\\interact}$, and a\ndriving %Jaynes-Cummings term '
        '$\\Op{H}_{d}$.\nterm.\nIn this paper, we consider a\nnetwork '
        'consisting of a series %cascade\nof cavities.\nThe network is '
        'depicted in \\Fig{network}.')
    result = format_latex(to_lines(text_in))
    assert result == expected
    assert(format_latex(to_lines(result))) == expected


def test_two_paragraphs():
    text_in = dedent(r'''
    In this paper, we consider a network consisting of a
    cascade of cavities.  The network is depicted in
    \Fig{network}.

    For a single node labeled $(i)$, the Hamiltonian
    consists of drift term $\Op{H}_0$, a static qubit-cavity
    interaction $\Op{H}_{\interact}$, and a driving
    Jaynes-Cummings term $\Op{H}_{d}$:
    ''').strip()
    expected = (
        'In this paper, we consider a network consisting of a cascade of '
        'cavities.\nThe network is depicted in \\Fig{network}.\n\nFor a '
        'single node labeled $(i)$, the Hamiltonian consists of drift '
        'term\n$\\Op{H}_0$, a static qubit-cavity interaction '
        '$\\Op{H}_{\\interact}$, and a\ndriving Jaynes-Cummings term '
        '$\\Op{H}_{d}$:')
    result = format_latex(to_lines(text_in))
    assert result == expected
    assert(format_latex(to_lines(result))) == expected


def test_equation():
    text_in = dedent(r'''
    For a single node labeled $(i)$, the Hamiltonian consists of drift term
    $\Op{H}_0$, a static qubit-cavity interaction $\Op{H}_{\interact}$, and a
    driving Jaynes-Cummings term $\Op{H}_{d}$. Leakage of photons out of the
    cavity is described by the Lindblad operator
    \begin{equation}
      \Op{L}^{(i)} = \sqrt{2 \kappa} \, \hat{a}_i\,.
    \end{equation}
    ''').strip()
    expected = (
        'For a single node labeled $(i)$, the Hamiltonian consists of drift '
        'term\n$\\Op{H}_0$, a static qubit-cavity interaction '
        '$\\Op{H}_{\\interact}$, and a\ndriving Jaynes-Cummings term '
        '$\\Op{H}_{d}$.\nLeakage of photons out of the cavity is described by '
        'the Lindblad operator\n\\begin{equation}\n  \\Op{L}^{(i)} '
        '= \\sqrt{2 \\kappa} \\, \\hat{a}_i\\,.\n\\end{equation}')
    result = format_latex(to_lines(text_in))
    assert result == expected
    assert(format_latex(to_lines(result))) == expected


def test_blank_lines():
    text_in = dedent(r'''
    \section{Model}

    \begin{figure}[tb]
    \end{figure}

    In this paper, we consider a
    network consisting of a cascade of cavities.
    The network is depicted in \Fig{network}.


    The second paragraph has an extra blank line.
    ''').strip()
    expected = (
        '\\section{Model}\n\n\\begin{figure}[tb]\n\\end{figure}\n\nIn this '
        'paper, we consider a network consisting of a cascade of '
        'cavities.\nThe network is depicted in \\Fig{network}.\n\n\nThe '
        'second paragraph has an extra blank line.')
    result = format_latex(to_lines(text_in))
    assert result == expected
    assert(format_latex(to_lines(result))) == expected
