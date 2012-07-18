
# Mmhhmmaaahhhhyyy precious...
.PRECIOUS: %.drs %.ccg

# Please set the following directories appropriately.
DIR_REASONER=$(HOME)/tmp/henry-n700
DIR_CONLL_DATA=$(HOME)/tmp/conll2011/conll-2011/v2/data
DIR_CANDC=/home/work/tools/ubuntu/semantic_parser/candc

DIR_PROGRAMS=./program

BSN=$(basename $@)
BSFN=$(basename $(notdir $@))

# MQP: Main Query Predicate
%.coref: %.lisp %.drs
	python $(DIR_PROGRAMS)/mycoref.py --input $(BSN).lisp --drs $(BSN).drs --reasoner $(DIR_REASONER)/bin/henry --target $(TARGET) $(OPTIONS)

%.lisp: %.drs
	perl $(DIR_PROGRAMS)/Boxer2Herny.pl --input $(BSN).drs --output /tmp/$(BSFN).henry
	python $(DIR_PROGRAMS)/henry2n700.py /tmp/$(BSFN).henry > /tmp/$(BSFN).lisp
	mv /tmp/$(BSFN).lisp $@

%.drs: %.ccg
	$(DIR_CANDC)/bin/boxer --input $(BSN).ccg --semantics tacitus > /tmp/$(BSFN).drs
	mv /tmp/$(BSFN).drs $@

%.ccg: %.txt
	$(DIR_CANDC)/bin/candc --models $(DIR_CANDC)/models/boxer --candc-printer boxer --input $(BSN).txt > /tmp/$(BSFN).ccg 2> $@.stderr
	mv /tmp/$(BSFN).ccg $@

%.txt:
	python $(DIR_PROGRAMS)/conll2txt.py --input `find $(DIR_CONLL_DATA)/$(BSN)/data/english/annotations -name '*.*auto_conll'` --format candc > /tmp/$(BSFN).txt
	mv /tmp/$(BSFN).txt $@

