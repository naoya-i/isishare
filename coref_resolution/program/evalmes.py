
import argparse, re, sys

def main():
	parser = argparse.ArgumentParser( description="Make it pretty!" )
	parser.add_argument( "--input", type=file, nargs="+", default=[sys.stdin] )
	parser.add_argument( "--measure", default="blanc" )
	parser.add_argument( "--format", default="fancy" )

	pa = parser.parse_args()
	
	for i, f in enumerate(pa.input):

		if "fancy" == pa.format:
			print "\33[1;40mSetting %d:\33[0m" % (1+i), f.name
			print "MEASURE".rjust(10), "RECALL".rjust(40), "PRECISION".rjust(40), "F1".rjust(20)
			print "-" * (10+40+40+20+4)
			
		ev = f.read()
		
		for i, vals in enumerate( re.findall( "(BLANC|Coreference): Recall: (.*?)\tPrecision: (.*?)\tF1: (.*?%)", ev ) ):
			if "fancy" == pa.format and pa.measure.upper() not in ["MUC", "B-CUBE", "CEAFM", "CEAFE", "BLANC"][i]: continue
			
			mes, rec, prec, f1 = vals
			
			if "fancy" == pa.format:
				print "\33[0;40m" if i%2 == 0 else "", ["MUC", "B-CUBE", "CEAFM", "CEAFE", "BLANC"][i].rjust(10), rec.rjust(40), prec.rjust(40), f1.rjust(20), "\33[0m"
				
			elif "tex" == pa.format and 2 != i:
				print "%.1f" % float(rec.split()[-1].replace("%", "")), "&", \
						"%.1f" % float(prec.split()[-1].replace("%", "")), "&", \
						"%.1f" % float(f1.replace("%", "")), "&",

		blanc = re.findall(
			"Coreference links: Recall: (.*?)\tPrecision: (.*?)\tF1: (.*?%)\n-+\n"+
			"Non-coreference links: Recall: (.*?)\tPrecision: (.*?)\tF1: (.*?%)\n-+\nBLANC", ev)

		if 0 < len(blanc): 
			if "fancy" == pa.format:
				print "", "BLANC-c".rjust(10), blanc[0][0].rjust(40), blanc[0][1].rjust(40), blanc[0][2].rjust(20)
				print "", "BLANC-nc".rjust(10), blanc[0][3].rjust(40), blanc[0][4].rjust(40), blanc[0][5].rjust(20)
							

		print
		
if "__main__" == __name__: main()
		
