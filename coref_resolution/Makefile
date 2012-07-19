
#
#   *  Please specify the following directories, or specify them when you run make.  *
#
DIR_REASONER         = $(HOME)/tmp/henry-n700
DIR_CONLL_DATA       = $(HOME)/tmp/conll2011/conll-2011/v2/data
DIR_CANDC            = /home/work/tools/ubuntu/semantic_parser/candc
DIR_STANFORD_CORENLP = $(HOME)/tmp/stanford-corenlp-2012-07-09

DIR_TMP              = /tmp
DIR_PROGRAMS         = ./program
DIR_DATA             = ./data
#
#                             ***
#

SHELL = /bin/zsh

# Mmhhmmaaahhhhyyy precious...
.PRECIOUS: %.drs %.ccg %.txt %.corenlp %.lisp

BSN   = $(basename $@)
BSFN  = $(basename $(notdir $@))

FILES_CONLL          = `find $(DIR_CONLL_DATA)/$(BSFN)/data/english/annotations -name '*.*auto_conll' $(FILES_CONLL_FILTER)`
FILES_CONLL_FILTER   = '| head -n2'

NUM_JOBS             = 2


# MQP: Main Query Predicate
%.coref: %.lisp %.drs %.txt knowledge_base
	echo '<?xml version="1.0"?>\n<coreference-output>' > $(DIR_TMP)/abcorefexp-$(BSFN).coref
	perl -nle "print "'$$1'" if /<META> '(.*?)'/" $(BSN).txt \
	| parallel -j $(NUM_JOBS) 'python $(DIR_PROGRAMS)/mycoref.py --input $(BSN).lisp --henry $(BSN).henry --drs $(BSN).drs --reasoner $(DIR_REASONER)/bin/henry \
									--target {} $(OPTIONS) --datadir $(DIR_DATA)' >> $(DIR_TMP)/abcorefexp-$(BSFN).coref
	echo '</coreference-output>' >> $(DIR_TMP)/abcorefexp-$(BSFN).coref
	mv $(DIR_TMP)/abcorefexp-$(BSFN).coref $@

knowledge_base: $(DIR_DATA)/kb.da

$(DIR_DATA)/kb.da:
	$(DIR_REASONER)/bin/henry -m compile_kb $(DIR_DATA)/wn-basic.lisp -o $@

%.lisp: %.drs %.corenlp
	foreach file (`perl -nle "print "'$$1'" if /<META> '(.*?)'/" $(BSN).txt`) \
		python -c "import sys, re; print \"\n\".join( re.findall(\"%%%%%%.*?\nid\('%s_[0-9]+',[0-9]+\)\.\n.*?\n\n\" % \"$$file\", sys.stdin.read(), re.DOTALL) )" < $(BSN).drs > xaxa.tmp.drs; \
		python -c "import sys, re; print re.findall(\"#begin %s\n(.*?)#end\" % \"$$file\", sys.stdin.read(), re.DOTALL)[0]" < $(BSN).corenlp > xaxa.corenlp; \
		baseid=`perl -nle 'print $$1 if /^([0-9]+) /' xaxa.tmp.drs | head -n1`; \
		python $(DIR_PROGRAMS)/shiftdrs.py --input xaxa.tmp.drs --baseid $$baseid > xaxa.drs; \
		perl $(DIR_PROGRAMS)/Boxer2Herny.pl --input xaxa.drs --coref xaxa.corenlp --output $(DIR_TMP)/abcorefexp-$(BSFN).tmp.henry; \
		cat $(DIR_TMP)/abcorefexp-$(BSFN).tmp.henry >> $(DIR_TMP)/abcorefexp-$(BSFN).henry; \
	end;
	python $(DIR_PROGRAMS)/henry2n700.py $(DIR_TMP)/abcorefexp-$(BSFN).henry > $(DIR_TMP)/abcorefexp-$(BSFN).lisp
	mv $(DIR_TMP)/abcorefexp-$(BSFN).lisp $(dir $@)/$(BSFN).lisp
	mv $(DIR_TMP)/abcorefexp-$(BSFN).henry $(dir $@)/$(BSFN).henry
	rm $(DIR_TMP)/abcorefexp-$(BSFN).tmp.henry xaxa.drs xaxa.tmp.drs xaxa.corenlp;

%.drs: %.ccg
	$(DIR_CANDC)/bin/boxer --input $(BSN).ccg --resolve true --semantics tacitus > $(DIR_TMP)/abcorefexp-$(BSFN).drs
	mv $(DIR_TMP)/abcorefexp-$(BSFN).drs $(dir $@)/$(BSFN).drs

%.ccg: %.txt
	$(DIR_CANDC)/bin/candc --models $(DIR_CANDC)/models/boxer --candc-printer boxer --input $(BSN).txt > $(DIR_TMP)/abcorefexp-$(BSFN).sentall.ccg
	python $(DIR_PROGRAMS)/chop4ccg.py --input $(DIR_TMP)/abcorefexp-$(BSFN).sentall.ccg > $@
	mv $(DIR_TMP)/abcorefexp-$(BSFN).sentall.ccg $(dir $@)/$(BSFN).sentall.ccg

%.txt:
	python $(DIR_PROGRAMS)/conll2txt.py --input $(FILES_CONLL) --format candc > $(DIR_TMP)/abcorefexp-$(BSFN).txt
	mv $(DIR_TMP)/abcorefexp-$(BSFN).txt $(dir $@)/$(BSFN).txt

%.corenlp: %.txt
	foreach file (`perl -nle "print "'$$1'" if /<META> '(.*?)'/" $(BSN).txt`) \
		echo "$(DIR_TMP)/abcorefexp-$$file.txt" >> $(DIR_TMP)/abcorefexp-$(BSFN).list.txt; \
		python -c "import re, sys; print re.findall( \"<META> '$$file'(.*?)\n\n\", sys.stdin.read(), re.DOTALL )[0]" < $(BSN).txt > $(DIR_TMP)/abcorefexp-$${file##*/}.txt; \
	end;
	cd $(DIR_STANFORD_CORENLP); \
	java -cp stanford-corenlp-2012-07-09.jar:stanford-corenlp-2012-07-06-models.jar:xom.jar:joda-time.jar \
	     -Xmx3g edu.stanford.nlp.pipeline.StanfordCoreNLP -annotators tokenize,ssplit,pos,lemma,ner,parse,dcoref -filelist $(DIR_TMP)/abcorefexp-$(BSFN).list.txt;
	echo -n "" > $(BSN).corenlp; \
	foreach file (`perl -nle "print "'$$1'" if /<META> '(.*?)'/" $(BSN).txt`) \
		echo "#begin $${file}" >> $(BSN).corenlp; \
		cat $(DIR_STANFORD_CORENLP)/abcorefexp-$$file.txt.xml >> $(BSN).corenlp; \
		echo "#end" >> $(BSN).corenlp; \
		rm $(DIR_STANFORD_CORENLP)/abcorefexp-$$file.txt.xml; \
	end;
	foreach file (`perl -nle "print "'$$1'" if /<META> '(.*?)'/" $(BSN).txt`) \
		rm $(DIR_TMP)/abcorefexp-$${file##*/}.txt; \
	end;
	rm $(DIR_TMP)/abcorefexp-$(BSFN).list.txt
