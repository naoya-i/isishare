SHELL = /bin/zsh

# Mmhhmmaaahhhhyyy precious...
.PRECIOUS: %.drs %.ccg


# Please set the following directories appropriately.
DIR_REASONER=$(HOME)/tmp/henry-n700
DIR_CONLL_DATA=$(HOME)/tmp/conll2011/conll-2011/v2/data
DIR_CANDC=/home/work/tools/ubuntu/semantic_parser/candc
DIR_STANFORD_CORENLP=$(HOME)/tmp/stanford-corenlp-2012-07-09

DIR_PROGRAMS=./program
DIR_DATA=./data

FILES_CONLL=`find $(DIR_CONLL_DATA)/$(BSFN)/data/english/annotations/nw -name '*.*auto_conll' | head -n2`

BSN=$(basename $@)
BSFN=$(basename $(notdir $@))

# MQP: Main Query Predicate
%.coref: %.lisp %.drs
	python $(DIR_PROGRAMS)/mycoref.py --input $(BSN).lisp --drs $(BSN).drs --reasoner $(DIR_REASONER)/bin/henry --target $(TARGET) $(OPTIONS)

%.lisp: %.drs %.corenlp
	foreach file (`perl -nle "print "'$$1'" if /<META> '(.*?)'/" $(BSN).txt`) \
		python -c "import sys, re; print re.findall(\"#begin %s.txt\n(.*?)#end\" % \"$$file\", sys.stdin.read(), re.DOTALL)[0]" < $(BSN).corenlp > xaxa.corenlp; \
		python -c "import sys, re; print \"\n\".join( re.findall(\"id\('%s_[0-9]+',[0-9]+\)\.\n.*?\n\n\" % \"$$file\", sys.stdin.read(), re.DOTALL) )" < $(BSN).drs > xaxa.drs; \
		perl $(DIR_PROGRAMS)/Boxer2Herny.pl --input xaxa.drs --coref xaxa.corenlp --output /tmp/$(BSFN).tmp.henry; \
		cat /tmp/$(BSFN).tmp.henry >> /tmp/$(BSFN).henry; \
	end;
	python $(DIR_PROGRAMS)/henry2n700.py /tmp/$(BSFN).henry > /tmp/$(BSFN).lisp
	mv /tmp/$(BSFN).lisp $@
	rm /tmp/$(BSFN).henry /tmp/$(BSFN).tmp.henry xaxa.drs xaxa.corenlp;

%.drs: %.ccg
	$(DIR_CANDC)/bin/boxer --input $(BSN).ccg --resolve true --semantics tacitus > /tmp/$(BSFN).drs
	mv /tmp/$(BSFN).drs $@

%.ccg: %.txt
	$(DIR_CANDC)/bin/candc --models $(DIR_CANDC)/models/boxer --candc-printer boxer --input $(BSN).txt > /tmp/$(BSFN).sentall.ccg
	python $(DIR_PROGRAMS)/chop4ccg.py --input /tmp/$(BSFN).sentall.ccg > $@
	mv /tmp/$(BSFN).sentall.ccg $(dir $@)

%.txt:
	python $(DIR_PROGRAMS)/conll2txt.py --input $(FILES_CONLL) --format candc > /tmp/$(BSFN).txt
	mv /tmp/$(BSFN).txt $@

%.corenlp: %.txt
	foreach file (`perl -nle "print "'$$1'" if /<META> '(.*?)'/" $(BSN).txt`) \
		echo "$(PWD)/$(DIR_DATA)/$$file.txt" >> /tmp/$(BSFN).list.txt; \
		python -c "import re, sys; print re.findall( \"<META> '$$file'(.*?)\n\n\", sys.stdin.read(), re.DOTALL )[0]" < $(BSN).txt > $(DIR_DATA)/$${file##*/}.txt; \
	end;
	mv /tmp/$(BSFN).list.txt ./$(DIR_DATA)/
	mypath=$(PWD); cd $(DIR_STANFORD_CORENLP); \
	java -cp stanford-corenlp-2012-07-09.jar:stanford-corenlp-2012-07-06-models.jar:xom.jar:joda-time.jar \
	     -Xmx3g edu.stanford.nlp.pipeline.StanfordCoreNLP -annotators tokenize,ssplit,pos,lemma,ner,parse,dcoref -filelist $$mypath/$(DIR_DATA)/$(BSFN).list.txt; \
	echo -n "" > $$mypath/$(DIR_DATA)/$(BSFN).corenlp; \
	foreach file (`cat $$mypath/$(DIR_DATA)/$(BSFN).list.txt`) \
		bsfile=$${file##*/}; \
		echo "#begin $${bsfile%%.v2_auto_conll.txt}" >> $$mypath/$(DIR_DATA)/$(BSFN).corenlp; \
		cat $$bsfile.xml >> $$mypath/$(DIR_DATA)/$(BSFN).corenlp; \
		echo "#end" >> $$mypath/$(DIR_DATA)/$(BSFN).corenlp; \
		rm $$bsfile.xml; \
	end;
	foreach file (`perl -nle "print "'$$1'" if /<META> '(.*?)'/" $(BSN).txt`) \
		rm $(DIR_DATA)/$${file##*/}.txt; \
	end;

