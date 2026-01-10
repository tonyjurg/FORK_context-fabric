TEX = intro-to-cf
PDF = $(TEX).pdf

.PHONY: all clean

all: $(PDF)

$(PDF): $(TEX).tex
	pdflatex -interaction=nonstopmode $(TEX).tex
	pdflatex -interaction=nonstopmode $(TEX).tex

clean:
	rm -f *.aux *.log *.out *.toc *.lof *.lot *.bbl *.blg
