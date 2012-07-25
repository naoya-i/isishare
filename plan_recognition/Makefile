SHELL=zsh

DIR_REASONER = $(HOME)/work/henry-n700

DIR_DATA     = ./data
DIR_PROGRAMS = ./program

BSN   = $(basename $@)
BSFN  = $(basename $(notdir $@))

NUM_LEARN_ITER = 50
R_TIMEOUT = 120

%.model:
	$(DIR_REASONER)/bin/henry -m learn ./data/mooney-kb.lisp ./data/mooney.e.lisp -e program/henryext.py -v3 -i cpi -t 8 -N $(NUM_LEARN_ITER) -d $(NUM_DEPTH) -T $(R_TIMEOUT) 2> $(BSN).stderr > $(BSN).stdout
	fgrep (model $(BSN).stdout | tail -n1 > $@

%.eval:
	perl -nle 'print $$1 if /target="(.*?)"/' $(BSN) > cl1.tmp
	perl -nle 'print $$1 if /<hypothesis.*?>(.*?)<\/hypothesis>/' $(BSN) > cl2.tmp
	perl -nle 'print $$1 if /gold-structure="(.*?)"/' $(BSN) > cl3.tmp
	paste cl[1-3].tmp | python $(DIR_PROGRAMS)/pr-evaluator.py > $@
	cat $@

graph_iter_vs_loss:
	perl -nle 'print $$1 if /Total loss: .*? \(avg. = ([0-9.]+)/' $(OUTPUT) | cat -n > tmp1
	perl -nle 'print $$1 if /Total loss: .*? \(avg. = ([0-9.]+)/' $(OUTPUT2) | cat -n > tmp2
	# perl -nle 'print $$1 if /Total loss: .*? \(avg. = ([0-9.]+)/' $(OUTPUT3) | cat -n > tmp3
	echo 'set terminal pdf; set size ratio 1; set xrange [0:$(MAX_ITER)]; set xlabel "Number of Iteration"; set ylabel "Averaged Loss"; plot "tmp1" with lp title "$(OUTPUT)", "tmp2" with lp title "$(OUTPUT2)", \
	"tmp3" with lp title "$(OUTPUT3)";' | gnuplot > ~/public_html/proofgraph.pdf                                                                                                                                                    
