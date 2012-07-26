
#
#   *  Please specify the following directories, or specify them when you run make.  *
#
DIR_REASONER         = $(HOME)/work/henry-n700
DIR_CONLL            = $(HOME)/tmp/conll2011/conll-2011
DIR_CONLL_SCORER     = $(HOME)/tmp/conll2011/conll-2011/scorer/v4
DIR_CANDC            = /home/work/tools/ubuntu/semantic_parser/candc
DIR_STANFORD_CORENLP = $(HOME)/tmp/stanford-corenlp-2012-07-09

DIR_TMP              = /tmp
DIR_PROGRAMS         = ./program
DIR_DATA             = ./data
#
#                             ***
#


PREP_OPTIONS = --coref xaxa.corenlp --nedis $(BSDIR)/$$file.aida
SHELL        = /bin/zsh

# Mmhhmmaaahhhhyyy precious...
.PRECIOUS: %.drs %.ccg %.txt %.corenlp %.henry %.lisp %.conllidx %.sentcoref %.coref %.gold %.aida

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

%.gold:
	file="$(BSFN)"; file=$${file%%-*}; \
	cat `find $(DIR_CONLL) -name "*$$file*_auto_conll"` > $@

%.conll: %.coref conll.idx
	python $(DIR_PROGRAMS)/mergecoref.py --input $(BSN).coref --conll-index conll.idx > $@

conll.idx:
	find $(DIR_CONLL) -name '*_auto_conll' | perl -nle 'print $$1 if /\/([^\/]+\..*?)$$/' > c1
	find $(DIR_CONLL) -name '*_auto_conll' > c2
	paste c1 c2 > $@
	rm c1 c2

%~0.sentcoref:
	echo

%.sentcoref:
	make `python -c 'x="$(BSN)".split("~"); print "%s~%s" % ("~".join(x[:-1]), int(x[-1])-1)'`.sentcoref
	sentid=`python -c 'print "$(BSFN)".split("~")[-1]'`; \
	bsn="$(BSN)";   bsn=$${bsn%%~*}; \
	bsfn="$(BSFN)"; bsfn=$${bsfn%%~*}; \
	python $(DIR_PROGRAMS)/mycoref.py\
	  --input $$bsn.lisp --henry $$bsn.henry --drs $$bsn.drs --reasoner $(DIR_REASONER)/bin/henry \
	  --target $$bsfn --sentence $$sentid $(OPTIONS) --datadir $(DIR_DATA) --extmod $(DIR_PROGRAMS)/henryext.py \
	  > $@
	#  --extcmd '--nedisj --wndisj --argcons --condunif $(DIR_DATA)/cu-boxer.kb $(DIR_DATA)/cu-adj.kb' > $@

%.coref: %.lisp %.drs %.txt $(DIR_DATA)/kb.da
	make $(BSN)~`perl -nle 'print $$1 if /\(O \(name (.*?)\)/' $(BSN).lisp | sort -rn | head -n1`.sentcoref
	echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<coreference-output>" > $@
	cat  $(BSN)~*.sentcoref >> $@
	echo "</coreference-output>" >> $@

$(DIR_DATA)/kb.da:
	$(DIR_REASONER)/bin/henry -m compile_kb $(DIR_DATA)/wn-basic.lisp -o $@

%.lisp: %.henry
	python $(DIR_PROGRAMS)/henry2n700.py $(BSN).henry | sort -nk3,3 > $@

%.henry: %.drs %.corenlp %.aida
	perl $(DIR_PROGRAMS)/Boxer2Herny.pl --coref $(BSN).corenlp --nedis $(BSN).aida --input $(BSN).drs --output $@

%.aida:
	java -jar program/AIDAinterface.jar input:$(BSN).txt output:$@

%.drs: %.ccg
	$(DIR_CANDC)/bin/boxer --input $(BSN).ccg --resolve true --semantics tacitus > $@

%.ccg: %.txt
	$(DIR_CANDC)/bin/candc --models $(DIR_CANDC)/models/boxer --candc-printer boxer --input $(BSN).txt > $@

%.tok: %.txt
	mypath=$(PWD); cd $(DIR_STANFORD_CORENLP); \
	java -cp stanford-corenlp-2012-07-09.jar:stanford-corenlp-2012-07-06-models.jar:xom.jar:joda-time.jar \
	  -Xmx3g edu.stanford.nlp.pipeline.StanfordCoreNLP -threads $(NUM_JOBS) -annotators tokenize,ssplit -file $$mypath/$(BSN).txt -outputDirectory $$mypath/$(BSDIR)
	perl $(DIR_PROGRAMS)/extract_tokenization.pl --input $(BSN).txt.xml --output $@

%.txt:
	f=$(BSFN); python $(DIR_PROGRAMS)/conll2txt.py --textid $(BSFN) \
	  --input `find $(DIR_CONLL)/*/data -name "$${f%%-*}.*_auto_conll"` > $@

%.corenlp: %.txt
	mypath=$(PWD); cd $(DIR_STANFORD_CORENLP); \
	java -cp stanford-corenlp-2012-07-09.jar:stanford-corenlp-2012-07-06-models.jar:xom.jar:joda-time.jar \
	  -Xmx3g edu.stanford.nlp.pipeline.StanfordCoreNLP -threads $(NUM_JOBS) \
	  -annotators tokenize,ssplit,pos,lemma,ner,parse,dcoref -file $$mypath/$(BSN).txt \
	  -outputDirectory $$mypath/$(BSDIR) -replaceExtension txt -outputExtension .corenlp
