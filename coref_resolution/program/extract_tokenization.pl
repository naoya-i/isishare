use strict;
use Getopt::Long;

my $ifile;
my $ofile;

GetOptions ("input=s" => \$ifile,
	    "output=s" => \$ofile);

if(($ifile eq "")||($ofile eq "")) {print("Input or output file missing.\n"); exit(0);}

open(IFILE,$ifile) or die "Cannot open $ifile\n";
open(OFILE,">".$ofile) or die "Cannot open $ofile\n";

my $first = 1;

while(my $line=<IFILE>){
   if($line =~ /<word>(.+)<\/word>/){
        my $word = $1;
        if($word eq "-LRB-") {$word = "(";}
        elsif($word eq "-RRB-") {$word = ")";}
        elsif($word =~ /^-(.+)-$/){print "Strange word: $word\n";}

        if($first == 1){$first = 0;}
        else{print OFILE " ";}

        print OFILE $word;
   }
   elsif($line =~ /<\/sentence>/){
   	print OFILE "\n";
        $first = 1;
   }
}

close IFILE;
close OFILE;