# Differential Analysis of Context Free Languages

This repository implements algorithms for differential analysis of Context Free Grammars, supporting the computation of an extension to Brzozowski Derivates for CFGs, and the application of this operation to parsing and recognition.

Traditional parsing algorithms have worked by considering nondeterministic traces througha language representation or else are dynamic programming algorithms which considerpartial parses on substrings to construct a final parse of the input string.  The approach outlined here looks instead at the language representation as dynamic, and seeks to leverage our capability of efficiently recognizing the nullability of an arbitrary context free grammar to decide whether some given string is contained inside a language.

This Repository is a work in progress. Look at branches besides master for features that still need some work. A better interface and documentation will be added in the near future...
