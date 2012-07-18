SHELL = /bin/zsh

# Mmhhmmaaahhhhyyy precious...
.PRECIOUS: %.drs %.ccg


# Please set the following directories appropriately.
DIR_REASONER=$(HOME)/tmp/henry-n700
DIR_CONLL_DATA=$(HOME)/tmp/conll2011/conll-2011/v2/data
DIR_CANDC=/home/work/tools/ubuntu/semantic_parser/candc
DIR_STANFORD_CORENLP=$(HOME)/tmp/stanford-corenlp-2012-07-09

DIR_PROGRAMS=./program

FILES_CONLL=`find $(DIR_CONLL_DATA)/$(BSFN)/data/english/annotations -name '*.*auto_conll' | head -n1`

BSN=$(basename $@)
BSFN=$(basename $(notdir $@))

# MQP: Main Query Predicate
%.coref: %.lisp %.drs
	python $(DIR_PROGRAMS)/mycoref.py --input $(BSN).lisp --drs $(BSN).drs --reasoner $(DIR_REASONER)/bin/henry --target $(TARGET) $(OPTIONS)

%.lisp: %.drs %.corenlp
	perl $(DIR_PROGRAMS)/Boxer2Herny.pl --input $(BSN).drs --coref $(BSN).corenlp --output /tmp/$(BSFN).henry
	python $(DIR_PROGRAMS)/henry2n700.py /tmp/$(BSFN).henry > /tmp/$(BSFN).lisp
	mv /tmp/$(BSFN).lisp $@
	rm /tmp/$(BSFN).henry

%.drs: %.ccg
	$(DIR_CANDC)/bin/boxer --input $(BSN).ccg --resolve true --semantics tacitus > /tmp/$(BSFN).drs
	mv /tmp/$(BSFN).drs $@

%.ccg: %.txt
	$(DIR_CANDC)/bin/candc --models $(DIR_CANDC)/models/boxer --candc-printer boxer --input $(BSN).txt > /tmp/$(BSFN).ccg
	mv /tmp/$(BSFN).ccg $@

%.txt:
	python $(DIR_PROGRAMS)/conll2txt.py --input $(FILES_CONLL) --format candc > /tmp/$(BSFN).txt
	mv /tmp/$(BSFN).txt $@

%.corenlp:
	foreach file ($(FILES_CONLL)) \
		python $(DIR_PROGRAMS)/conll2txt.py --input $$file > ./data/$${file##*/}.txt; \
		echo "$(PWD)/data/$${file##*/}.txt" >> /tmp/$(BSFN).list.txt; \
	end;
	mv /tmp/$(BSFN).list.txt ./data/
	\
	mypath=$(PWD); cd $(DIR_STANFORD_CORENLP); \
	java -cp stanford-corenlp-2012-07-09.jar:stanford-corenlp-2012-07-06-models.jar:xom.jar:joda-time.jar \
	     -Xmx3g edu.stanford.nlp.pipeline.StanfordCoreNLP -annotators tokenize,ssplit,pos,lemma,ner,parse,dcoref -filelist $$mypath/data/$(BSFN).list.txt; \
	\
	echo -n "" > $$mypath/data/$(BSFN).corenlp; \
	foreach file (`cat $$mypath/data/$(BSFN).list.txt`) \
		echo "#begin $${file##*/}.xml" >> $$mypath/data/$(BSFN).corenlp; \
		cat $${file##*/}.xml >> $$mypath/data/$(BSFN).corenlp; \
		echo "#end" >> $$mypath/data/$(BSFN).corenlp; \
	end;

