# Copyright (C) 2013 Itzik Kotler
#
# This file is part of Hackersh.
#
# Hackersh is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# Hackersh is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Hackersh; see the file COPYING.  If not,
# see <http://www.gnu.org/licenses/>.
#
# Based on invRegex.py (http://pyparsing.wikispaces.com/file/view/invRegex.py) by Paul McGuire

from pyparsing import Literal, oneOf, printables, ParserElement, Combine, SkipTo, operatorPrecedence, ParseFatalException, Word, nums, opAssoc, Suppress, ParseResults, srange


# Local imports

import hackersh.components


# Metadata

__author__ = "Itzik Kotler <xorninja@gmail.com>"
__version__ = "0.1.0"


#################
# <invRegex.py> #
#################

class CharacterRangeEmitter(object):

    def __init__(self, chars):
        # remove duplicate chars in character range, but preserve original order
        seen = set()
        self.charset = "".join(seen.add(c) or c for c in chars if c not in seen)

    def __str__(self):
        return '[' + self.charset + ']'

    def __repr__(self):
        return '[' + self.charset + ']'

    def makeGenerator(self):
        def genChars():
            for s in self.charset:
                yield s
        return genChars


class OptionalEmitter(object):

    def __init__(self, expr):
        self.expr = expr

    def makeGenerator(self):
        def optionalGen():
            yield ""
            for s in self.expr.makeGenerator()():
                yield s
        return optionalGen


class DotEmitter(object):

    def makeGenerator(self):
        def dotGen():
            for c in printables:
                yield c
        return dotGen


class GroupEmitter(object):

    def __init__(self, exprs):
        self.exprs = ParseResults(exprs)

    def makeGenerator(self):
        def groupGen():
            def recurseList(elist):
                if len(elist) == 1:
                    for s in elist[0].makeGenerator()():
                        yield s
                else:
                    for s in elist[0].makeGenerator()():
                        for s2 in recurseList(elist[1:]):
                            yield s + s2
            if self.exprs:
                for s in recurseList(self.exprs):
                    yield s
        return groupGen


class AlternativeEmitter(object):

    def __init__(self, exprs):
        self.exprs = exprs

    def makeGenerator(self):
        def altGen():
            for e in self.exprs:
                for s in e.makeGenerator()():
                    yield s
        return altGen


class LiteralEmitter(object):

    def __init__(self, lit):
        self.lit = lit

    def __str__(self):
        return "Lit:" + self.lit

    def __repr__(self):
        return "Lit:" + self.lit

    def makeGenerator(self):
        def litGen():
            yield self.lit
        return litGen


def handleRange(toks):
    return CharacterRangeEmitter(srange(toks[0]))


def handleRepetition(toks):
    toks = toks[0]
    if toks[1] in "*+":
        raise ParseFatalException("", 0, "unbounded repetition operators not supported")
    if toks[1] == "?":
        return OptionalEmitter(toks[0])
    if "count" in toks:
        return GroupEmitter([toks[0]] * int(toks.count))
    if "minCount" in toks:
        mincount = int(toks.minCount)
        maxcount = int(toks.maxCount)
        optcount = maxcount - mincount
        if optcount:
            opt = OptionalEmitter(toks[0])
            for i in range(1, optcount):
                opt = OptionalEmitter(GroupEmitter([toks[0], opt]))
            return GroupEmitter([toks[0]] * mincount + [opt])
        else:
            return [toks[0]] * mincount


def handleLiteral(toks):
    lit = ""
    for t in toks:
        if t[0] == "\\":
            if t[1] == "t":
                lit += '\t'
            else:
                lit += t[1]
        else:
            lit += t
    return LiteralEmitter(lit)


def handleMacro(toks):
    macroChar = toks[0][1]
    if macroChar == "d":
        return CharacterRangeEmitter("0123456789")
    elif macroChar == "w":
        return CharacterRangeEmitter(srange("[A-Za-z0-9_]"))
    elif macroChar == "s":
        return LiteralEmitter(" ")
    else:
        raise ParseFatalException("", 0, "unsupported macro character (" + macroChar + ")")


def handleSequence(toks):
    return GroupEmitter(toks[0])


def handleDot():
    return CharacterRangeEmitter(printables)


def handleAlternative(toks):
    return AlternativeEmitter(toks[0])


_parser = None


def parser():
    global _parser
    if _parser is None:
        ParserElement.setDefaultWhitespaceChars("")
        lbrack, rbrack, lbrace, rbrace, lparen, rparen = map(Literal, "[]{}()")

        reMacro = Combine("\\" + oneOf(list("dws")))
        escapedChar = ~reMacro + Combine("\\" + oneOf(list(printables)))
        reLiteralChar = "".join(c for c in printables if c not in r"\[]{}().*?+|") + " \t"

        reRange = Combine(lbrack + SkipTo(rbrack, ignore=escapedChar) + rbrack)
        reLiteral = (escapedChar | oneOf(list(reLiteralChar)))
        reDot = Literal(".")
        repetition = (
            (lbrace + Word(nums).setResultsName("count") + rbrace) |
            (lbrace + Word(nums).setResultsName("minCount") + "," + Word(nums).setResultsName("maxCount") + rbrace) |
            oneOf(list("*+?"))
        )

        reRange.setParseAction(handleRange)
        reLiteral.setParseAction(handleLiteral)
        reMacro.setParseAction(handleMacro)
        reDot.setParseAction(handleDot)

        reTerm = (reLiteral | reRange | reMacro | reDot)
        reExpr = operatorPrecedence(reTerm,
                                    [
                                        (repetition, 1, opAssoc.LEFT, handleRepetition),
                                        (None, 2, opAssoc.LEFT, handleSequence),
                                        (Suppress('|'), 2, opAssoc.LEFT, handleAlternative),
                                    ]
                                    )
        _parser = reExpr

    return _parser


def count(gen):
    """Simple function to count the number of elements returned by a generator."""
    i = 0
    for s in gen:
        i += 1
    return i


def invert(regex):
    """Call this routine as a generator to return all the strings that
       match the input regular expression.
           for s in invert("[A-Z]{3}\d{3}"):
               print s
    """
    invReGenerator = GroupEmitter(parser().parseString(regex)).makeGenerator()
    return invReGenerator()

##################
# </invRegex.py> #
##################


# Implementation

class RegexExpand(hackersh.components.RootComponent):

    """Expand a Regular Expression (String) Into All the Possible Matching Strings"""

    def main(self, argv, context):

        _context = []

        for s in invert(argv[0]):

            _context.append(dict({'__STDIN__': s}))

        return _context

    DISPLAY_NAME = "regex_expand"
