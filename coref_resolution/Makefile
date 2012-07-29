
#
#   *  Please specify the following directories, or specify them when you run make.  *
#
DIR_REASONER          = $(HOME)/work/henry-n700
DIR_CONLL             = $(HOME)/tmp/conll2011/conll-2011
DIR_CONLL_SCORER      = $(HOME)/tmp/conll2011/conll-2011/scorer/v4
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


PREP_OPTIONS = --coref xaxa.corenlp --nedis $(BSDIR)/$$file.aida
SHELL        = /bin/zsh

# Mmhhmmaaahhhhyyy precious...
.PRECIOUS: %.drs %.ccg %.txt %.corenlp %.henry %.lisp %.conllidx %.sentcoref %.coref %.gold %.aida %.tok %.conll %.allconll %.allcoref

BSN   = $(basename $@)
BSFN  = $(basename $(notdir $@))
BSDIR = $(dir $@)

NUM_JOBS             = 16
EVAL_MEASURE         = muc

# MQP: Main Query Predicate
%.eval: %.conll %.coref %.gold
	pwd=$(PWD); \
	cd $(DIR_CONLL_SCORER); \
	perl scorer.pl $(EVAL_MEASURE) $$pwd/$(BSN).gold $$pwd/$(BSN).conll;

%.evalall: %.allconll %.allcoref %.gold
	pwd=$(PWD); \
	cd $(DIR_CONLL_SCORER); \
	perl scorer.pl $(EVAL_MEASURE) $$pwd/$(BSN).gold $$pwd/$(BSN).allconll;

%.gold: %.allcoref
	file="$(BSFN)"; file=$${file%%-*}; \
	if grep -q coreference-result $(BSN).allcoref; then; \
	cat `find $(DIR_CONLL) -name "*$$file*_auto_conll"` | python $(DIR_PROGRAMS)/conll2txt.py --textid $(BSFN) --format conll > $@; \
	fi

%.conll: %.coref conll.idx
	python $(DIR_PROGRAMS)/mergecoref.py --input $(BSN).coref --conll-index conll.idx --goldmention > $@

%.allconll: %.allcoref conll.idx
	python $(DIR_PROGRAMS)/mergecoref.py --input $(BSN).allcoref --conll-index conll.idx --goldmention > $@

%.exe: conll.docs
	$(MAKE) `awk '{print "evaluation/" $$0 ".$(BSFN)" }' < conll.docs`

conll.docs:
	cat `find $(DIR_CONLL)/*/data/dev/data/english/annotations/*/*/*/ -name '*auto_conll'` | perl -nle "print \$$1 . '_' . \$$2 . '-' . \$$3 if /\/([a-z]+)_(.*?)\); part ([0-9]+)/" $(DOCS_FILTER) > $@

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
	  --input $$bsn.lisp --henry $$bsn.henry --drs $$bsn.drs --reasoner $(DIR_REASONER)/bin/henry \
	  --target $$bsfn --sentence $$sentid $(OPTIONS) --datadir $(DIR_DATA) --extmod $(DIR_PROGRAMS)/henryext.py \
	  --extcmd '--nedisj --wndisj --argcons --condunif $(DIR_DATA)/cu-boxer.kb $(DIR_DATA)/cu-adj.kb' >> $@
	#  > $@

%.allcoref: %.lisp
	echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<coreference-output>" > $@
	bsn="$(BSN)";   bsn=$${bsn%%~*}; \
	bsfn="$(BSFN)"; bsfn=$${bsfn%%~*}; \
	python $(DIR_PROGRAMS)/mycoref.py\
	  --input $$bsn.lisp --henry $$bsn.henry --drs $$bsn.drs --reasoner $(DIR_REASONER)/bin/henry \
	  --target $$bsfn --sentence 0 $(OPTIONS) --datadir $(DIR_DATA) --extmod $(DIR_PROGRAMS)/henryext.py \
	  >> $@
	#  --extcmd '--nedisj --wndisj --argcons --condunif $(DIR_DATA)/cu-boxer.kb $(DIR_DATA)/cu-adj.kb' >> $@
	echo "</coreference-output>" >> $@

%.coref: %.lisp %.drs %.txt $(DIR_DATA)/kb.da
	$(MAKE) $(BSN)~`perl -nle 'print $$1 if /\(O \(name (.*?)\)/' $(BSN).lisp | sort -rn | head -n1`.sentcoref
	echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<coreference-output>" > $@
	cat  $(BSN)~*.sentcoref >> $@
	echo "</coreference-output>" >> $@

$(DIR_DATA)/kb.da:
	$(DIR_REASONER)/bin/henry -m compile_kb $(DIR_DATA)/wn-basic.lisp -o $@

%.lisp: %.henry
	python $(DIR_PROGRAMS)/henry2n700.py $(BSN).henry | sort -nk3,3 > $@
	perl -nle "print \$$1 if /\(\^(.*)\) \)$$/" $@ | awk '{printf $$0}' > $@.allsent
	echo -n "(O (name 0) (^ " >> $@
	cat $@.allsent >> $@
	echo ") )" >> $@
	rm $@.allsent

%.henry: %.drs %.corenlp
	perl $(DIR_PROGRAMS)/Boxer2Herny.pl --coref $(BSN).corenlp --input $(BSN).drs --output $@ #--nedis $(BSN).aida 

%.aida:
	java -jar program/AIDAinterface.jar input:$(BSN).txt output:$@

%.drs: %.ccg
	$(DIR_CANDC)/bin/boxer --input $(BSN).ccg --resolve true --semantics tacitus > $@

%.ccg: %.tok
	$(DIR_CANDC)/bin/soap_client --url "localhost:$(CANDC_SOAP_PORT)" --input $(BSN).tok > $@ #$(DIR_CANDC)/bin/candc --models $(DIR_CANDC)/models/boxer --candc-printer boxer --input $(BSN).tok > $@

%.tok: %.txt
	python $(DIR_PROGRAMS)/cscorenlp.py --port $(CS_CORENLP_TOK_PORT) --cmd parse --input $(BSN).txt > $@.xml
	perl $(DIR_PROGRAMS)/extract_tokenization.pl --input $@.xml --output $@
	rm $@.xml

%.txt:
	f=$(BSFN); python $(DIR_PROGRAMS)/conll2txt.py --textid $(BSFN) \
	  --input `find $(DIR_CONLL)/*/data -name "$${f%%-*}.*_auto_conll"` > $@

%.corenlp: %.txt
	python $(DIR_PROGRAMS)/cscorenlp.py --port $(CS_CORENLP_COREF_PORT) --cmd parse --input $(BSN).txt > $@


