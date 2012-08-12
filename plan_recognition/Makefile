SHELL=zsh

SIGN=$@.d$(DEPTH).i$(ILP_INFMETHOD).ic$(ILP_CORE).it$(ILP_TIMEOUT).$(PKG)
DIR_REASONER = $(HOME)/work/henry-n700

DIR_DATA     = ./data
DIR_PROGRAMS = ./program

BSN   = $(basename $@)
BSFN  = $(basename $(notdir $@))

NUM_LEARN_ITER = 50
R_TIMEOUT = 120

speed_table:
	fgrep prepare= $(OUTPUT).stdout | perl -nle 'print $$1, "\t", $$2, "\t", $$3 if /total="([0-9.]+)" prepare="([0-9.]+)" ilp="([0-9.]+)"/' | awk '{x+=$$1; y+=$$2; z+=$$3; n++} END{print x/n, y/n, z/n, n}'
	fgrep prepare= $(OUTPUT).stdout | perl -nle 'print $$1, "\t", $$2, "\t", $$3 if /total="([0-9.]+)" prepare="([0-9.]+)" ilp="([0-9.]+)"/' | awk '$$2 < 120 {x+=$$1; y+=$$2; z+=$$3; n++} END{printf "%.2f (", y/n }'
	python -c "import sys; sys.stdout.write( \"%.1f \\%%) & \" % (100.0 * `perl -nle 'print $$1 if /prepare=\"([0-9.]+)\"/' < $(OUTPUT).stdout | awk '$$1 > 0 && $$1 < 120' | wc -l` / `grep 'solution=\"' $(OUTPUT).stdout | wc -l`) );"
	fgrep prepare= $(OUTPUT).stdout | perl -nle 'print $$1, "\t", $$2, "\t", $$3 if /total="([0-9.]+)" prepare="([0-9.]+)" ilp="([0-9.]+)"/' | awk '$$3 > 0 && $$3 < 120 {x+=$$1; y+=$$2; z+=$$3; n++} END{printf "%.2f (", z/n }'
	python -c "import sys; sys.stdout.write( \"%.1f \\%%) & \" % (100.0 * `perl -nle 'print $$1 if /ilp=\"([0-9.]+)\"/' < $(OUTPUT).stdout | awk '$$1 > 0 && $$1 < 120' | wc -l` / `grep 'solution=\"' $(OUTPUT).stdout | wc -l`) );"
	fgrep '"Optimal"' $(OUTPUT).stdout | fgrep constraints | perl -nle 'print $$1 if /constraints="([0-9]+)/' | awk '{x+=$$1; n++} END{printf "%d", x/n }'
	fgrep 'Finished: Activated' $(OUTPUT).stderr | perl -nle 'print $$1 if /([0-9]+)/' | awk '{x+=$$1; n++} END{if( 0==n ) print " \\\\"; else printf " ($$\\Delta$$ %d) \\\\\n", x/n; }'

speed_test_mooney:
	seq -f 'e%g' 1 25 | parallel -j $(NUM_JOBS) '$(DIR_REASONER)/bin/henry -m infer $(DIR_DATA)/score-function.lisp $(DIR_DATA)/mooney-kb.lisp $(DIR_DATA)/mooney.e.lisp -e program/henryext.py -p {} -i $(ILP_INFMETHOD) -v3 -t $(ILP_CORE) -T $(ILP_TIMEOUT) -d $(DEPTH) -c wa' \
	> result/$(SIGN).stdout 2> result/$(SIGN).stderr
	# seq -f 't%g' 1 25 | parallel -j $(NUM_JOBS) '$(DIR_REASONER)/bin/henry -m infer $(DIR_DATA)/score-function.lisp $(DIR_DATA)/mooney-kb.lisp $(DIR_DATA)/mooney.t.lisp -e program/henryext.py -p {} -i $(ILP_INFMETHOD) -v3 -t $(ILP_CORE) -T $(ILP_TIMEOUT) -d $(DEPTH) -c wa' \
	# >> result/$(SIGN).stdout 2>> result/$(SIGN).stderr

dataset:
	python $(DIR_PROGRAMS)/mooney-o2henry.py --input $(DIR_DATA)/data-pr-test.lisp --tlp $(DIR_DATA)/singla-top-level-plans.txt > $(DIR_DATA)/mooney.t.lisp
	python $(DIR_PROGRAMS)/mooney-o2henry.py --input $(DIR_DATA)/data-pr-train.lisp --tlp $(DIR_DATA)/singla-top-level-plans.txt > $(DIR_DATA)/mooney.e.lisp

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
