
#
#   *  Please specify the following directories, or specify them when you run make.  *
#
DIR_REASONER          = $(HOME)/work/henry-n700
DIR_CONLL             = /work/naoya-i/conll-2012
DIR_CONLL_SCORER      = /work/naoya-i/conll-2012/scorer/v4
DIR_CONLL_TYPE        = dev
DIR_CANDC             = /home/work/tools/ubuntu/semantic_parser/candc
DIR_STANFORD_CORENLP  = $(HOME)/tmp/stanford-corenlp-2012-07-09

DIR_TMP               = /tmp
DIR_PROGRAMS          = ./program
DIR_DATA              = ./data

CANDC_SOAP_PORT       = 9000
CS_CORENLP_TOK_PORT   = 9001
CS_CORENLP_COREF_PORT = 9002
#
#                             ***
#

DEPTH        = 0
SHELL        = /bin/zsh
REFRESH      = 0

BSN        = $(basename $@)
BSFN       = $(basename $(notdir $@))
BSDIR      = $(dir $@)
BSNWOPKG   = $(subst $(PKG),,$(BSN))
BSFNWOPKG  = $(subst $(PKG),,$(BSFN))

NUM_JOBS             = 16
EVAL_MEASURE         = all

# Build options.
ifneq (,$(findstring SCN,$(SETTING)))
FLAGS_B2H +=--coref $(BSNWOPKG).corenlp
else
FLAGS_B2H +=--wholefileoutput 1
endif

ifneq (,$(findstring AIDA,$(SETTING)))
FLAGS_B2H +=--nedis $(BSNWOPKG).aida 
endif

# Mmhhmmaaahhhhyyy precious...
.PRECIOUS: %.drs %.ccg %.txt %.corenlp %.lisp %.conllidx %.sentcoref %.coref %.gold %.aida %.tok %.conll %.conll-allsent %.coref-allsent %.gold-allsent

# MQP: Main Query Predicate
%.evaluate:
	mkdir -p $(BSDIR)
	if expr $(REFRESH) = 1; then; touch $(BSN)/$(PKG)tmp.conll-allsent; touch $(BSN)/tmp.gold-allsent; rm -f $(BSN)/*.gold-allsent $(BSN)/$(PKG)*.conll-allsent; fi
	$(MAKE) $(BSN).docs
	$(MAKE) `awk '{print "$(BSN)/$(PKG)" $$0 ".conll-allsent" }' < $(BSN).docs` `awk '{print "$(BSN)/$(PKG)" $$0 ".gold-allsent" }' < $(BSN).docs`
	cat $(BSN)/*.gold-allsent > tmp.gold-allsent
	cat $(BSN)/$(PKG)*.conll-allsent > tmp.conll-allsent
	echo "Evaluating..."
	pwd=$(PWD); \
	cd $(DIR_CONLL_SCORER); \
	perl scorer.pl $(EVAL_MEASURE) $$pwd/tmp.gold-allsent $$pwd/tmp.conll-allsent;
	rm tmp.gold-allsent tmp.conll-allsent

%.eval: %.conll %.coref %.gold
	echo ";-)"

%.score:
	if expr $(REFRESH) = 1; then; rm -f $(BSN).coref-allsent $(BSN).conll-allsent $(BSNWOPKG).gold-allsent; fi
	$(MAKE) $(BSN).conll-allsent $(BSNWOPKG).gold-allsent
	cd /work/naoya-i/conll-2012/scorer/v4; \
	perl scorer.pl $(EVAL_MEASURE) $(BSNWOPKG).gold-allsent $(BSN).conll-allsent

%.gold: 
	file="$(BSFN)"; file=$${file%%-*}; \
	#if grep -q coreference-result $(BSN).coref; then;
	cat `find $(DIR_CONLL) -name "*$$file*_auto_conll"` | python $(DIR_PROGRAMS)/conll2txt.py --textid $(BSFN) --format conll > $@; \
	#fi

%.gold-allsent:
	if fgrep -q "Optimal" $(BSN).coref-allsent; then; \
		cat `find $(DIR_CONLL) -name "*$$file*_auto_conll"` | python $(DIR_PROGRAMS)/conll2txt.py --textid $(BSFNWOPKG) --format conll > $@; \
	fi;
	# if ! fgrep -q "ARE MISSING" $(BSN).ccg; then; \
	# 	cat `find $(DIR_CONLL) -name "*$$file*_auto_conll"` | python $(DIR_PROGRAMS)/conll2txt.py --textid $(BSFN) --format conll > $@; \
	# fi;
	#cat `find $(DIR_CONLL) -name "*$$file*_auto_conll"` | python $(DIR_PROGRAMS)/conll2txt.py --textid $(BSFN) --format conll > $@

wao:
	file="$(BSFN)"; file=$${file%%-*}; \
	if grep -q coreference-result $(BSDIR)$(PKG)$(BSFN).coref-allsent; then; \
	cat `find $(DIR_CONLL) -name "*$$file*_auto_conll"` | python $(DIR_PROGRAMS)/conll2txt.py --textid $(BSFN) --format conll > $@; \
	fi
	#rm $@.txt $@.txt.xml; \
	# java -cp $(DIR_STANFORD_CORENLP)/stanford-corenlp-2012-07-09.jar:$(DIR_STANFORD_CORENLP)/stanford-corenlp-2012-07-06-models.jar:$(DIR_STANFORD_CORENLP)/xom.jar:$(DIR_STANFORD_CORENLP)/joda-time.jar \
	# 	-Xmx3g edu.stanford.nlp.pipeline.StanfordCoreNLP -annotators tokenize,ssplit -file $@.txt -outputDirectory $(BSDIR); \
	#cat `find $(DIR_CONLL) -name "*$$file*_auto_conll"` | python $(DIR_PROGRAMS)/conll2txt.py --textid $(BSFN) --format raw > $@.txt; \

%.conll: %.coref conll.idx
	python $(DIR_PROGRAMS)/mergecoref.py --input $(BSN).coref --conll-index conll.idx --goldmention > $@

%.conll-allsent: conll.idx
	if expr $(REFRESH) = 1; then; rm -f $(BSN).coref-allsent; fi
	$(MAKE) $(BSN).coref-allsent
	python $(DIR_PROGRAMS)/mergecoref.py --input $(BSN).coref-allsent --conll-index conll.idx --goldmention > $@

%.docs:
	cat `find $(DIR_CONLL)/*/data/$(DIR_CONLL_TYPE)/data/english/annotations/*/*/*/ -name '*auto_conll'` | perl -nle "print \$$1 . '_' . \$$2 . '-' . \$$3 if /\/([a-z0-9]+)_(.*?)\); part ([0-9]+)/" $(DOCS_FILTER) > $@

conll.idx:
	find $(DIR_CONLL) -name '*_auto_conll' | perl -nle 'print $$1 if /\/([^\/]+\..*?)$$/' > c1
	find $(DIR_CONLL) -name '*_auto_conll' > c2
	paste c1 c2 > $@
	rm c1 c2

%~0.sentcoref:
	echo

%.sentcoref:
	$(MAKE) `python -c 'x="$(BSN)".split("~"); print "%s~%s" % ("~".join(x[:-1]), int(x[-1])-1)'`.sentcoref
	sentid=`python -c 'print "$(BSFN)".split("~")[-1]'`; \
	bsn="$(BSN)";   bsn=$${bsn%%~*}; \
	bsfn="$(BSFN)"; bsfn=$${bsfn%%~*}; \
	python $(DIR_PROGRAMS)/mycoref.py\
	  --input $$bsn.lisp --henry $$bsn.henry --reasoner $(DIR_REASONER)/bin/henry \
	  --target $$bsfn --sentence $$sentid $(OPTIONS) --datadir $(DIR_DATA) --extmod $(DIR_PROGRAMS)/henryext.py \
	  --extcmd '--nedisj --wndisj --argcons --condunif $(DIR_DATA)/cu-boxer.kb $(DIR_DATA)/cu-adj.kb' >> $@
	#  > $@

%.coref-allsent:
	$(MAKE) $(BSN).lisp
	echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<coreference-output>" > $@
	bsn="$(BSN)";   bsn=$${bsn%%~*}; \
	bsnwopkg="$(BSNWOPKG)"; bsnwopkg=$${bsnwopkg%%~*}; \
	bsfn="$(BSFNWOPKG)"; bsfn=$${bsfn%%~*}; \
	python $(DIR_PROGRAMS)/mycoref.py\
	  --input $$bsn.lisp --reasoner $(DIR_REASONER)/bin/henry \
	  --target $$bsfn --sentence 0 $(OPTIONS) --datadir $(DIR_DATA) --depth $(DEPTH) --extmod $(DIR_PROGRAMS)/henryext.py \
	  --extcmd '$(EXTCMD) ' --anythingelse '$(ANYTHINGELSE) ' >> $@ \
	#  >> $@
	echo "</coreference-output>" >> $@

%.coref: %.lisp %.drs %.txt $(DIR_DATA)/kb.da
	$(MAKE) $(BSN)~`perl -nle 'print $$1 if /\(O \(name (.*?)\)/' $(BSN).lisp | sort -rn | head -n1`.sentcoref
	echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<coreference-output>" > $@
	cat  $(BSN)~*.sentcoref >> $@
	echo "</coreference-output>" >> $@

$(DIR_DATA)/kb.da:
	$(DIR_REASONER)/bin/henry -m compile_kb $(DIR_DATA)/wn-ent.lisp $(DIR_DATA)/wn-mm.lisp $(DIR_DATA)/wn-cs.lisp $(DIR_DATA)/wn-hyp.lisp $(DIR_DATA)/fn-mt1r.lisp $(DIR_DATA)/fn-rel.lisp $(DIR_DATA)/fn-sr.lisp -o $@

$(DIR_DATA)/kb-wnfn.da:
	$(DIR_REASONER)/bin/henry -m compile_kb $(DIR_DATA)/wn-ent.lisp $(DIR_DATA)/wn-mm.lisp $(DIR_DATA)/wn-cs.lisp $(DIR_DATA)/wn-hyp.lisp $(DIR_DATA)/wn-der.lisp $(DIR_DATA)/fn-mt1r.lisp $(DIR_DATA)/fn-rel.lisp -o $@

%.lisp: conll.idx
	$(MAKE) $(BSNWOPKG).drs
	perl $(DIR_PROGRAMS)/Boxer2Henry.pl --input $(BSNWOPKG).drs --output $@.com $(FLAGS_B2H)
	cat $@.com | sed "s/' / /g" | perl -ple 's/\((loc|org|nam|per|ttl) /(\@$$1 /g' | perl -ple 's/\((neuter|thing|male|female|his) /(~$$1 /g' | perl -ple 's/\((not|pos|nec) /($$1-M /g' | python -c 'import sys; print sys.stdin.read()[:-2]' > $@
	echo "  (label (^" >> $@
	python $(DIR_PROGRAMS)/make-train.py --input $(BSNWOPKG).drs --textid $(BSFNWOPKG) --conll-index conll.idx >> $@
	echo "  ) ) )" >> $@
	rm $@.com

%.aida:
	java -jar program/AIDAinterface.jar input:$(BSN).txt output:$@

%.drs: %.ccg
	$(DIR_CANDC)/bin/boxer --input $(BSN).ccg --resolve false --modal true --semantics tacitus > $@

%.ccg: %.tok
	$(DIR_CANDC)/bin/soap_client --url "localhost:$(CANDC_SOAP_PORT)" --input $(BSN).tok > $@
	err=`expr \`wc -l $(BSN).tok | cut -f1 -d' '\` - \`awk '$$0 ~ /ccg\([0-9]+/' $@ | wc -l | cut -f1 -d' '\``; \
	if expr $$err != 0; then; \
		echo "" >> $@; \
		echo "% $$err SENTENCE(S) ARE MISSING." >> $@; \
	fi

%.tok: %.txt
	cp $(BSN).txt $@

%.txt:
	f=$(BSFN); python $(DIR_PROGRAMS)/conll2txt.py --textid $(BSFN) \
	  --input `find $(DIR_CONLL)/*/data -name "$${f%%-*}.*_auto_conll"` > $@

%.corenlp: %.txt
	python $(DIR_PROGRAMS)/cscorenlp.py --port $(CS_CORENLP_COREF_PORT) --cmd parse --input $(BSN).txt > $@

%.losscurve:
	bsn='$(BSN)'; perl -nle 'print $$1 if /averaged-loss="([0-9e.-]+)"/' $${bsn#.*} | cat -n > tmp1
	echo 'set terminal pdf; set size ratio 1; set xrange [0:$(MAX_ITER)]; set xlabel "Number of Iteration"; set ylabel "Averaged Loss"; plot "tmp1" with lp title "$(T1)", "tmp2" with lp title "$(T2)", \
	"tmp3" with lp title "$(OUTPUT3)";' | gnuplot > ~/public_html/proofgraph.pdf
	mv tmp1 tmp2

%.xyplot:
	echo 'set terminal pdf; set size ratio 1; set xrange [0:$(MAX_ITER)]; set xlabel "Number of Iteration"; set xlabel "$(XLABEL)"; set ylabel "$(YLABEL)"; plot "$(BSN)" with lp title "$(T)";' | gnuplot > ~/public_html/proofgraph.pdf

%.dataset:
	find $(BSN) -name "*.tok" > fl-$(BSFN).tmp
	split -d -l 80 fl-$(BSFN).tmp fl-$(BSFN).tmp.
	foreach f (`ls fl-$(BSFN).tmp.*`); \
		java -cp $(DIR_STANFORD_CORENLP)/stanford-corenlp-2012-07-09.jar:$(DIR_STANFORD_CORENLP)/stanford-corenlp-2012-07-06-models.jar:$(DIR_STANFORD_CORENLP)/xom.jar:$(DIR_STANFORD_CORENLP)/joda-time.jar \
		-Xmx4g edu.stanford.nlp.pipeline.StanfordCoreNLP -annotators tokenize,ssplit,pos,lemma,ner,parse,dcoref -props ./data/corenlp-altok.conf -filelist $$f \
		-outputDirectory $(BSN) -extension .tok -replaceExtension .tok -outputExtension .corenlp -threads $(NUM_JOBS) -noClobber \
		2>> $(BSN).$$f.corenlplog.stderr >> $(BSN).$$f.corenlplog.stdout &; \
	end;



fancy:
	python ~/work/henry-n700/tools/proofgraph.py --input l | /usr/bin/dot -Tpdf > ~/public_html/proofgraph.pdf
	python ~/work/henry-n700/tools/proofgraph.py --input l --format html > ~/public_html/