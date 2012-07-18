use strict;
use Data::Dumper;
use Getopt::Long;

my %conditional = ();
my %regex_conditional = ();
my %nonmerge = ();
my %id2props = ();
my %args2props = ();
my %count_words_before = ();

my $ifile = "";
my $ofile = "";
my $cfile = "";
my $sfile = "";
my $nefile = "";
my $nonmerge_opt = "";

my $cost = "1";
my $split = 0;
my $samepred = 0;
my $sameargs = 0;
my $modality = 0;


GetOptions ("input=s" => \$ifile,
	    "output=s" => \$ofile,
	    "conditional=s" => \$cfile,
            "coref=s" => \$sfile,
            "nedis=s" => \$nefile,
            "cost=s" => \$cost,
            "split=i" => \$split,
            "nonmerge=s" => \$nonmerge_opt);

&setParameters();

&read_Conditional_file();

open(OUT,">$ofile") or die "Cannot open $ofile\n";

&read_Boxer_file();

## ADD COREF INFO FROM STANDFORD NLP
&add_coref();

## ADD NE DISAMBIGUATION INFO FROM STANDFORD NLP
&add_nedis();

## IF COREF OR NE INFO WAS ADDED THEN PRINT OUT (OTHEWISE IT HAS BEEN ALREADY PRINTED OUT)
if(($sfile ne "")||($nefile ne "")){&add_nm_and_printAll();}

close OUT;

###########################################################################
# ADD NON MERGE AND PRINT ALL
###########################################################################

sub add_nm_and_printAll(){
    ## ADD NONMERGE CONSTRAINTS AND PRINT OUT HENRY FORMAT SENCENCE BY SENTENCE
    for my $sid (sort (keys %id2props)){
	    print "Processing sentence $sid...\n";
	    &add_nonmerge($sid);
	    &printHenryFormat($sid);
	    %nonmerge = ();
    }
    print "Henry file printed.\n";
}

###########################################################################
# SET PARAMETERS
###########################################################################

sub setParameters(){
   if(($ifile eq "")||($ofile eq "")) {print("Input or output file missing.\n"); &printUsage();}

   if(($split!=0)&&($split!=1)) {print("Wrong value of 'split' parameter: $split. Only '0' and '1' accepted.\n"); exit(0);}

   if($cost !~ /\d+(.\d+)?/) {print("Wrong value of 'cost' parameter: $cost. Only real numbers accepted.\n"); exit(0);}

   if($nonmerge_opt ne ""){
   	my @data = split(/,/,$nonmerge_opt);
        foreach my $d (@data){
        	&setNMParameter($d);
        }
   }
}

sub setNMParameter(){
   my ($p) = @_;

   if($p eq "modality") {$modality = 1;}
   elsif($p eq "samepred") {$samepred = 1;}
   elsif($p eq "sameargs") {$sameargs = 1;}
   else{print("Wrong value of 'nonmerge' parameter: $p. Only 'modality', 'samepred', and 'sameargs' accepted.\n"); exit(0);}
}

###########################################################################
# PRING USAGE
###########################################################################

sub printUsage(){
    print "Usage: perl Boxer2Henry.pl\n --input <boxer file>\n --output <henry file>\n --cost <real number> (default=1)\n [--conditional <conditional unification file>]\n [--coref <standford coref file>]\n [--nedis <disambiguated named entities file>]\n [--split <split nouns concatenated by Boxer> (possible values: [0=no, 1=yes], default: 0)]\n [--non-merge <nonmerge options> (possible values:modality,samepred,sameargs) 'modality' -- consider modality to create non-merge, 'samepred' -- non-merge for props with the same name, 'sameargs' -- non-merge for args of the same prop] \n";
    exit(0);
}

###########################################################################
# ADD NAMED ENTITIES DISAMBIGUATION INFO
###########################################################################

my %nedis_info = ();

sub add_nedis(){
     if($nefile eq "") {return;}

     &read_nedis_file();

     my $constant_counter = 0;

    foreach my $entity (keys %nedis_info){
         $constant_counter++;
         my $new_predname = lc($entity)."-nn'";
         $new_predname =~ s/_/-/g;

         my %been = ();

         foreach my $key (keys %{$nedis_info{$entity}}){
              for (my $i=$nedis_info{$entity}{$key}{'start'}; $i<=$nedis_info{$entity}{$key}{'end'};$i++){
                   my $sid = $nedis_info{$entity}{$key}{'sid'};
                   my $boxer_tid = $sid * 1000 + $i;

                   if(exists $id2props{$sid}{$boxer_tid}){
                        for my $pname (keys %{$id2props{$sid}{$boxer_tid}}){
                                 my @args =  @{$id2props{$sid}{$boxer_tid}{$pname}{'args'}};
                                 if((scalar @args)==2){
                                      # REPLACE ARGS WITH A NEW CONSTANT
                                      if(!(exists $been{$args[1]})){
                                        $been{$args[1]} = 1;

                                        &replace_args($args[0],"E".$constant_counter,"");
                                        &replace_args($args[1],"NE".$constant_counter,"");
                                      }
	                         }
                        }
                        delete($id2props{$sid}{$boxer_tid});
                        foreach my $a (keys %{$args2props{$sid}}){
                            delete($args2props{$sid}{$a}{$boxer_tid});
                        }
                   }
                   $id2props{$sid}{$boxer_tid}{$new_predname}{'args'} = ["E".$constant_counter,"NE".$constant_counter];
                   $args2props{$sid}{"E".$constant_counter}{$boxer_tid}{$new_predname}{'0'} = 1;
                   $args2props{$sid}{"NE".$constant_counter}{$boxer_tid}{$new_predname}{'1'} = 1;
              }
         }
    }

}

###########################################################################
# ADD NAMED ENTITIES DISAMBIGUATION INFO
###########################################################################

sub read_nedis_file(){
    open(FILE,$nefile) or die "Cannot open $nefile\n";

    my $nedis_counter = 0;

    while(my $line=<FILE>){
         if($line =~ /([^\s]+):(\d+)-(\d+) -> ([^\s\n]+)/){
         	my $sid = $1;
                my $start_id = $2;
                my $end_id = $3;
                my $entity = $4;

                if(($entity ne "--NME--")&&($entity !~ /\\/)){
                	$nedis_counter++;

                	$nedis_info{$entity}{$nedis_counter}{'sid'} = $sid;
                	$nedis_info{$entity}{$nedis_counter}{'start'} = $start_id - $count_words_before{$sid};
                	$nedis_info{$entity}{$nedis_counter}{'end'} = $end_id - $count_words_before{$sid};
                }
         }
         else{
         	print "Strange NE line: $line";
         }
    }

    close FILE;

    print "Disambiguated named entities file read.\n";
}

###########################################################################
# ADD COREF INFO
###########################################################################

my %coref_info = ();

sub add_coref(){

    if($sfile eq "") {return;}

    &read_coref_file();

    my $constant_counter = 0;

    #print OUT Dumper(%id2props);  exit(0);

    foreach my $key (keys %coref_info){
        $constant_counter++;
        my %been = ();

        foreach my $sid (keys %{$coref_info{$key}}){
             foreach my $tid (keys %{$coref_info{$key}{$sid}}){
                  my $boxer_tid = $sid * 1000 + $tid;

                  if(exists $id2props{$sid}{$boxer_tid}){
                        for my $pname (keys %{$id2props{$sid}{$boxer_tid}}){
                        	my @args =  @{$id2props{$sid}{$boxer_tid}{$pname}{'args'}};

	                        my $arg = "";

	                        if((scalar @args)==2){
	                              $arg = $args[1];
	                        }
	                        elsif($pname =~ /^of-in/){
	                              $arg = $args[2];
	                        }
	                        else{
	                                print "Another coref element ($sid, $boxer_tid): $pname\n";
	                        }

                                # REPLACE ARGS WITH A NEW CONSTANT
	                        if($arg ne ""){
                                   if(!(exists $been{$arg})){
                                        $been{$arg} = 1;
                                        &replace_args($arg,"C".$constant_counter,$sid);
                                   }
                                }
                        }
                  }
             }
        }
    }

    #print OUT Dumper(%id2props); exit(0);
    print "Coreference information added.\n";
}

###########################################################################
# REPLACE ARGS
###########################################################################

sub replace_args(){
    my ($arg,$newarg,$sid) = @_;

    if($sid ne ""){
    	foreach my $aid (keys %{$args2props{$sid}{$arg}}){
	            foreach my $ap (keys %{$args2props{$sid}{$arg}{$aid}}){
	                    foreach my $aind (keys %{$args2props{$sid}{$arg}{$aid}{$ap}}){
                                       if(exists $id2props{$sid}{$aid}{$ap}){
                                       		$id2props{$sid}{$aid}{$ap}{'args'}[$aind] = $newarg;
                                       }
	                    }
	            }
	}
	$args2props{$sid}{$newarg} = delete $args2props{$sid}{$arg};
    }
    else{
       foreach my $s (keys %args2props){
          &replace_args($arg,$newarg,$s);
       }
    }
}

###########################################################################
# READ COREF FILE
###########################################################################

sub read_coref_file(){
    open(FILE,$sfile) or die "Cannot open $sfile\n";

    my $sid = "";
    my $tid = "";
    my %id2word = ();
    my $coref_counter = -1;
    my $coref_flag = 0;

    my $coref_sid;
    my $coref_head;

    while(my $line=<FILE>){
         if($line =~ /<sentence id="(\d+)">/){
         	$sid = $1;
         }
         elsif($line =~ /<token id="(\d+)">/){
                $tid = $1;
         }
         elsif($line =~ /<word>(.+)<\/word>/){
         	my $word = $1;
                $id2word{$sid}{$tid} = $word;
         }
         elsif($line =~ /<coreference>/){
                $coref_counter++;
                $coref_flag = 1;
         }
         elsif(($coref_flag==1)&&($line =~ /<sentence>(\d+)<\/sentence>/)){
                $coref_sid = $1;
         }
         elsif(($coref_flag==1)&&($line =~ /<head>(\d+)<\/head>/)){
                my $coref_tid = $1;
                $coref_info{$coref_counter}{$coref_sid}{$coref_tid} = $id2word{$coref_sid}{$coref_tid};
         }
    }

    close FILE;
    %id2word = ();

    print "Coference file read.\n";
}


###########################################################################
# ADD NON-MERGE CONSTRAINTS
###########################################################################

sub add_nonmerge(){
   my ($sent_id) = @_;

   if(($modality+$samepred+$sameargs)==0) {return;}

   my @pids = keys %{$id2props{$sent_id}};

   #CHECK CONDITIONAL AND MODALITY IN ADVANCE
   if(($samepred==1)||($modality==1)){
        for my $pid (@pids){
	        for my $pname (keys %{$id2props{$sent_id}{$pid}}){
                        if($samepred==1){
                        	$id2props{$sent_id}{$pid}{$pname}{'cond'} = &check_conditional($pname,(scalar @{$id2props{$sent_id}{$pid}{$pname}{'args'}}));
                        }

                        if($modality==1){
                                $id2props{$sent_id}{$pid}{$pname}{'mod'} = &define_modality($sent_id,$pid,$pname);
                        }
	        }
	}
   }

   foreach(my $i=0;$i<(scalar @pids);$i++){
        my $pid1 = $pids[$i];
        for my $pname1 (keys %{$id2props{$sent_id}{$pid1}}){
              my @args =  @{$id2props{$sent_id}{$pid1}{$pname1}{'args'}};

              ## ARGUMENTS OF THE SAME PREDICATE CANNOT BE MERGED
              if($sameargs == 1){
              		foreach(my $i=0;$i<(scalar @args);$i++){
	                      my $arg1 = $args[$i];
	                      foreach(my $j=$i+1;$j<(scalar @args);$j++){
	                         my $arg2 = $args[$j];
	                         if($arg1 ne $arg2){
	                                if(!(exists $nonmerge{$arg2."!=".$arg1})){
	                                        $nonmerge{$arg1."!=".$arg2} = 1;
	                                }
	                         }
	                      }
	               }
               }
               ############################################

               ## FIRST ARGUMENTS OF PREDICATES HAVING THE SAME NAME OR
               ## DIFFERENT MODALITY CANNOT BE MERGED (EXCLUDING CONDITIONAL UNIFICATION PREDICATES)

               #print Dumper($id2props{'1'}); exit(0);

               if((($samepred==1)||($modality==1))&&($id2props{$sent_id}{$pid1}{$pname1}{'cond'} == 0)){
                     foreach(my $j=$i+1;$j<(scalar @pids);$j++){
        		my $pid2 = $pids[$j];
        		for my $pname2 (keys %{$id2props{$sent_id}{$pid2}}){
                           if($pname2 ne "WORD"){
                             ## SAME PREDICATES CANNOT BE MERGED
                             if(($samepred==1)&&($pname1 eq $pname2)){
                                #print "$pid1 $pid2 $pname1\n";
                                my $a1 = $args[0];
	                        my $a2 = $id2props{$sent_id}{$pid2}{$pname2}{'args'}[0];
	                        if($a1 ne $a2){
	                                if(!(exists $nonmerge{$a2."!=".$a1})){
                                                $nonmerge{$a1."!=".$a2} = 1;
	                                }
	                        }
	                     }
                             ## DIFFERENT MODALITIES CANNOT BE MERGED
                             elsif(($modality==1)&&(&check_modality_clash($sent_id,$pid1,$pname1,$pid2,$pname2)==1)){
                                 my $a1 = $args[0];
	                         my $a2 = $id2props{$sent_id}{$pid2}{$pname2}{'args'}[0];
	                         if($a1 ne $a2){
	                         	if(!(exists $nonmerge{$a2."!=".$a1})){
                                                $nonmerge{$a1."!=".$a2} = 1;
	                                }
	                         }
                             }
                           }
                        }
                     }
               }
        }
   }
}

###########################################################################
# CHECL MODALITY CLASH
###########################################################################

sub check_modality_clash(){
    my ($sent_id,$pid1,$pname1,$pid2,$pname2) = @_;

    my $pos1 = $id2props{$sent_id}{$pid1}{$pname1}{'pos'};
    my $pos2 = $id2props{$sent_id}{$pid1}{$pname1}{'pos'};

    if(($pos1 eq "n")||($pos2 eq "n")){
    	return 0;
    }

    if($pos1 ne $pos2){
    	return 0;
    }

    my $mod1 = $id2props{$sent_id}{$pid1}{$pname1}{'mod'};
    my $mod2 = $id2props{$sent_id}{$pid2}{$pname2}{'mod'};

    if($mod1 ne $mod2) {return 1;}

    return 0;
}

###########################################################################
# DEFINE MODALITY
###########################################################################

sub define_modality(){
   my ($sent_id,$pid,$pname) = @_;

   if($id2props{$sent_id}{$pid}{$pname}{'pos'} eq "n") {return "";}

   my $arg1 = $id2props{$sent_id}{$pid}{$pname}{'args'}[0];


   for my $pid2 (keys %{$id2props{$sent_id}}){
        if($pid ne $pid2){
        	for my $pname2 (keys %{$id2props{$sent_id}{$pid2}}){
                     if(($id2props{$sent_id}{$pid2}{$pname2}{'pos'} ne "p")&&($pname2 ne "rel'")){
                           my @args2 = @{$id2props{$sent_id}{$pid2}{$pname2}{'args'}};
	                   foreach(my $k=1;$k<(scalar @args2);$k++){
	                        if($args2[$k] eq $arg1){
	                             return $pid2.$pname2;
	                        }
	                   }
                    }
        	}
        }
   }

   return "";
}
###########################################################################
# CREATE FINAL OUTPUT
###########################################################################

sub printHenryFormat(){
    my ($sent_id) = @_;

    my $str = $sent_id . "] ";

    my $id_counter = 1;

    my %out_str = ();

    foreach my $pid (keys %{$id2props{$sent_id}}){
         foreach my $pname (keys %{$id2props{$sent_id}{$pid}}){
                       my @args = @{$id2props{$sent_id}{$pid}{$pname}{'args'}};
                       my $key = $pname.",".$args[0];
                       if(!(exists $out_str{$key})){
                            my $pred_str = $pname . "(";
                            foreach my $arg (@args){
	                        $pred_str = $pred_str . $arg . ",";
	               	    }
	               	    chop($pred_str);
                            $pred_str = $pred_str . "):$cost:$sent_id-$id_counter";

                            $out_str{$key}{'pred'} = $pred_str;
                       }
                       push(@{$out_str{$key}{'pids'}},$pid);
    	}
    }


    foreach my $key (keys %out_str){
        $id_counter++;
        $str = $str . $out_str{$key}{'pred'} . ":[";
        foreach my $pid (@{$out_str{$key}{'pids'}}){
           $str = $str . $pid . ",";
        }
        chop($str);
        $str = $str . "] & ";
    }

    foreach my $nm (keys %nonmerge){
    	$str = $str . $nm . " & ";
    }

    chop($str);chop($str);chop($str);
    print OUT $str . "\n";

    %out_str = ();
}

###########################################################################
# READ CONDITIONAL FILE INTO A STRUCTURE
###########################################################################
sub read_Conditional_file(){
    if($cfile eq "") {return;}

   open(CFILE,$cfile) or die "Cannot open $cfile \n";
   while(my $line=<CFILE>){
     if($line =~ /set_condition\(\/(.+)\/(\d+):/){
     	my $regexp_name = $1;
        my $arity = $2;

        $regex_conditional{$regexp_name} = $arity;
     }
     elsif($line =~ /set_condition\((.+)\/(\d+):/){
        my $name = $1;
        my $arity = $2;

        $conditional{$name} = $arity;
     }
   }
   close(CFILE);

   print "Conditional unification predicates file read\n";
}

###########################################################################
# CHECK IF CONDITIONAL
###########################################################################

sub check_conditional(){
	my ($pred,$arity) = @_;

        if(exists $conditional{$pred}){
        	if($conditional{$pred}==$arity){return 1;}
                else{return 0;}
        }

        foreach my $regex (keys %regex_conditional){
            if($pred =~ /$regex/){
               if($regex_conditional{$regex}==$arity){return 1;}
               else{return 0;}
            }
        }

        return 0;
}

###########################################################################
# READ BOXER FILE INTO A STRUCTURE, ADD NONMERGE CONSTRAINTS, OUTPUT
###########################################################################
sub read_Boxer_file(){
    my $ne_count = 0;
    my $new_id = 0;
    my $sent_id = "";
    my $word_counter = 0;

    open(IN,$ifile) or die "Cannot open $ifile\n";
    while(my $line=<IN>){
       if($line =~ /^%%%/){

       }
       elsif($line =~ /^id\((.+),\d+\)\.\n/){
           if(($sent_id ne "")&&((scalar keys %id2props)==0)){
    		print "No props for sent: $sent_id \n";
    	   }

           if(($sfile eq "")&&($nefile eq "")){
                print "Processing sentence $sent_id.\n";
	    	&add_nonmerge($sent_id);
	   	&printHenryFormat($sent_id);
                %id2props = ();
           }

           $sent_id = $1;
           $sent_id =~ s/ //g;
           $sent_id =~ s/'//g;
           $ne_count = 0;

           $count_words_before{$sent_id} = $word_counter;
       }
       elsif($line =~ /(\d+) ([^\s]+) [^\s]+ [^\s]+ [^\s]+/){
           #if(($sfile ne "")||($nefile ne "")){
           #       my $id = $1;
	   #       my $word = $2;
	   #       $id2props{$sent_id}{$id}{'WORD'} = $word;
           #}
           $word_counter++;
       }
       elsif($line ne "\n"){
           my @prop_str = split(" & ", $line);
           foreach my $p (@prop_str){
                my $name;
                my @args;
                my $id_str="";
                my @ids = ();

                if($p =~ /\[(.*)\]:([^\(]+)\(([^\)]+)\)/){
                        $id_str = $1;
                        $name = lc($2);
                	@args = split(/,/,$3);
                }
                else{
                	print "Strange propositions: $p\n";
                }

                if($id_str eq ""){
                	$new_id++;
                        push(@ids,"$sent_id-ID$new_id");
                }
                else{
                    @ids = $id_str =~ /(\d+)/g;
                }

                for (my $i=0;$i<(scalar @args);$i++){
                	$args[$i]=$sent_id.$args[$i];
                }

                $name =~ s/ /-/g;
                $name =~ s/_/-/g;
                $name =~ s/:/-/g;
                $name =~ s/\./-/g;
                $name =~ s/\//-/g;

                if($name =~ /(.+)-([a-z])$/){  ## THERE IS A PREFIX
                  my $prefix = $1;
                  my $postfix = $2;

                  my $newpostfix;

                  if($postfix eq "n"){
                      $newpostfix = "nn";
                  }
                  elsif($postfix eq "v"){
                      $newpostfix = "vb";
                  }
                  elsif($postfix eq "a"){
                      $newpostfix = "adj";
                  }
                  elsif($postfix eq "r"){
                      $newpostfix = "rb";
                  }
                  elsif($postfix eq "p"){
                      $newpostfix = "in";
                  }
                  else{
                  	print "Strange postfix: $prefix-$postfix in sent $sent_id \n";
                        $newpostfix = $postfix;
                  }

                  if ($prefix =~ /[\w\d]/){ ## IT IS A NORMAL PREDICATE, NOT JUST SOME SYMBOLS
                       if(($split==1)&&(($postfix eq "n")&&($prefix =~ /-/))){ ## A NOUN NEEDS TO BE SPLIT
                           my @nns = split("-",$prefix);
                           for (my $i=0; $i<(scalar @nns);$i++){
                        	if($i==(scalar @nns)-1){
                                    my $lname = $nns[$i]."-nn'";

                                    foreach my $id (@ids){
                                    	$id2props{$sent_id}{$id}{$lname}{'args'} = [@args];
                                    	$id2props{$sent_id}{$id}{$lname}{'pos'} = "n";

                                        if(($sfile ne "")||($nefile ne "")){
                                		# CREATE args2props
                                                $args2props{$sent_id}{$args[0]}{$id}{$lname}{'0'} = 1;
                                        	$args2props{$sent_id}{$args[1]}{$id}{$lname}{'1'} = 1;
                                        }
                                    }
                                }
                                else{
                                    my $ne_count++;
                                    my $lname = $nns[$i]."-".$newpostfix."'";

                                    foreach my $id (@ids){
                                    	$id2props{$sent_id}{$id}{$lname}{'args'} = [$sent_id."ne".$ne_count,$args[1]];
                                    	$id2props{$sent_id}{$id}{$lname}{'pos'} = "n";

                                        if(($sfile ne "")||($nefile ne "")){
                                		# CREATE args2props
                                                $args2props{$sent_id}{$args[0]}{$id}{$lname}{'0'} = 1;
                                        	$args2props{$sent_id}{$args[1]}{$id}{$lname}{'1'} = 1;
                                        }
                                    }
                                }
                           }
                       }
                       else{  ## NO NEED TO SPLIT
                                my $lname = $prefix."-".$newpostfix."'";

                                foreach my $id (@ids){
                                    	$id2props{$sent_id}{$id}{$lname}{'args'} = [@args];
                                    	$id2props{$sent_id}{$id}{$lname}{'pos'} = $postfix;

                                        if(($sfile ne "")||($nefile ne "")){
                                		# CREATE args2props
                                                for (my $i=0;$i<(scalar @args);$i++){
                                                        $args2props{$sent_id}{$args[$i]}{$id}{$lname}{$i} = 1;
                                                }
                                        }
                                }
                       }
                  }
           	}
                else{	##THERE IS NO POSTFIX
                   if ($name =~ /[\w\d]/){  ## IT IS A NORMAL PREDICATE, NOT JUST SOME SYMBOLS
                        $name = &check_prep($name);  ## CHECK IF IT IS A PROPOSITION
                        my $lname = $name."'";

                        foreach my $id (@ids){
                                    	$id2props{$sent_id}{$id}{$lname}{'args'} = [@args];
                                    	$id2props{$sent_id}{$id}{$lname}{'pos'} = "";

                                        if(($sfile ne "")||($nefile ne "")){
                                		# CREATE args2props
                                                for (my $i=0;$i<(scalar @args);$i++){
                                                        $args2props{$sent_id}{$args[$i]}{$id}{$lname}{$i} = 1;
                                                }
                                        }
                        }
                   }
                }
           }
       }
    }
    close IN;

    if(($sent_id ne "")&&((scalar keys %id2props)==0)){
    		print "No props for sent: $sent_id \n";
    }

    if(($sfile eq "")&&($nefile eq "")){
    	print "Processing sentence $sent_id.\n";
	&add_nonmerge($sent_id);
	&printHenryFormat($sent_id);
        %id2props = ();
    }

    print "Boxer file read.\n";
}
################################################################################
# CHECK IF BOXER DID NOT RECOGNIZE SOME PREPOSITIONS AS SUCH
################################################################################
sub check_prep()
{
  my ($predname) = @_;

  my @prepositions = (
	"abaft",
	"aboard",
	"about",
	"above",
	"absent",
	"across",
	"afore",
	"after",
	"against",
	"along",
	"alongside",
	"amid",
	"amidst",
	"among",
	"amongst",
	"around",
	"as",
	"aside",
	"astride",
	"at",
	"athwart",
	"atop",
	"barring",
	"before",
	"behind",
	"below",
	"beneath",
	"beside",
	"besides",
	"between",
	"betwixt",
	"beyond",
	"but",
	"by",
	"concerning",
	"despite",
	"during",
	"except",
	"excluding",
	"failing",
	"following",
	"for",
	"from",
	"given",
	"in",
	"including",
	"inside",
	"into",
	"lest",
	"like",
	"minus",
	"modulo",
	"near",
	"next",
	"of",
	"off",
	"on",
	"onto",
	"opposite",
	"out",
	"outside",
	"over",
	"pace",
	"past",
	"plus",
	"pro",
	"qua",
	"regarding",
	"round",
	"sans",
	"save",
	"since",
	"than",
	"through",
	"throughout",
	"till",
	"times",
	"to",
	"toward",
	"towards",
	"under",
	"underneath",
	"unlike",
	"until",
	"up",
	"upon",
	"versus",
	"via",
	"vice",
	"with",
	"within",
	"without",
	"worth",
	);

  foreach my $preposition (@prepositions){
       if($predname eq $preposition){
                #print $predname . "\n";
       		return $predname."-in";
       }
  }

   return $predname;
}