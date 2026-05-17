# Minimal Makefile for the paper. Requires latexmk + a TeX distribution
# with amsart, amsmath, hyperref, cleveref, booktabs, xcolor, enumitem.
# (todonotes is NOT used — the paper uses \stub via \providecommand in
# preamble.tex.)

TARGET := main
LATEXMK := latexmk -pdf -interaction=nonstopmode -halt-on-error

.PHONY: all watch clean distclean final

all:
	$(LATEXMK) $(TARGET).tex

# Live preview: rebuilds on any .tex/.bib change. Requires latexmk -pvc.
watch:
	$(LATEXMK) -pvc $(TARGET).tex

# Clean intermediate files but keep the final PDF.
clean:
	latexmk -c $(TARGET).tex
	rm -f *.bbl *.synctex.gz sections/*.aux appendices/*.aux

# Wipe everything including the PDF.
distclean:
	latexmk -C $(TARGET).tex
	rm -f *.bbl *.synctex.gz sections/*.aux appendices/*.aux

# Final-submission build: append a \renewcommand that makes \stub swallow
# its argument, so the orange [TODO] boxes disappear from the PDF. Run
# from a clean checkout; the .bak file ensures the original preamble is
# restored after the build.
final:
	cp preamble.tex preamble.tex.bak
	echo '\renewcommand{\stub}[1]{}% disabled for final build' >> preamble.tex
	$(LATEXMK) $(TARGET).tex
	mv preamble.tex.bak preamble.tex
