# on phos: /opt/common/CentOS_6/python/python-2.7.8/bin/python
#
# /opt/common/CentOS_6/python/python-2.7.8/bin/python /home/wilson/FACETS/scripts/add_sample_atts.py \
#  -f Proj_08390_OUT.txt \
#  -p /ifs/res/pi/Proj_08390.c881d62c-9e7a-11e8-859a-645106ef9e4c/portal/data_clinical_sample.txt \
#  -g Proj_08390___HISENS_GeneCalls_v2.txt > data_clinical_sample.txt
#
# Writes to stdout a new data_clinical.txt file

import getopt
import sys
import os.path
import csv
import re

# TODO this should be replaced by something better
expected_facets_columns = ["Sample", "Facets", "snp.nbhd", "ndepth", "purity_cval", "cval", "min.nhet", "genome", "Purity", "Ploidy", "dipLogR", "loglik", "flags"]
facets_column_definitions = [["FACETS: Version", "FACETS: SNP NBHD", "FACETS: N Depth", "FACETS: Purity C-Val", "FACETS: C-Val", "FACETS: Min N Het", "FACETS: Genome", "FACETS: Purity", "FACETS: Ploidy", "FACETS: Dip Log R", "FACETS: Log LIK", "FACETS: Flags", "FACETS: WGD"], ["FACETS: Version", "FACETS: SNP NBHD", "FACETS: N Depth", "FACETS: Purity C-Val", "FACETS: C-Val", "FACETS: Min N Het", "FACETS: Genome", "FACETS: Purity", "FACETS: Ploidy", "FACETS: Dip Log R", "FACETS: Log LIK", "FACETS: Flags", "FACETS: Whole Genome Duplication"], ["STRING", "NUMBER", "NUMBER", "NUMBER", "NUMBER", "NUMBER", "STRING", "NUMBER", "NUMBER", "NUMBER", "NUMBER", "STRING", "STRING"], ["1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1"]]
GENE_CALLS_SAMPLE_COLUMN_INDEX = 0
GENE_CALLS_WGD_COLUMN_INDEX = 13

def run(facets_filename, portal_filename, gene_calls_filename, verbose):

  sample_to_wgd = {}
  # read in gene calls file
  with open(gene_calls_filename, 'r') as gene_calls_file:
    gene_calls_reader = csv.reader(gene_calls_file, delimiter='\t')
    gene_calls_header = gene_calls_reader.next()

    if gene_calls_header[GENE_CALLS_SAMPLE_COLUMN_INDEX] != "Tumor_Sample_Barcode":
      print >>sys.stderr, "ERROR: expected column '%s' to be 'Tumor_Sample_Barcode' in '%s'" % (gene_calls_header[GENE_CALLS_SAMPLE_COLUMN_INDEX], gene_calls_filename)
      sys.exit(2)

    if gene_calls_header[GENE_CALLS_WGD_COLUMN_INDEX] != "WGD":
      print >>sys.stderr, "ERROR: expected column '%s' to be 'WGD' in '%s'" % (gene_calls_header[GENE_CALLS_WGD_COLUMN_INDEX], gene_calls_filename)
      sys.exit(2)

    for row in gene_calls_reader:
      sample_to_wgd[row[GENE_CALLS_SAMPLE_COLUMN_INDEX]] = row[GENE_CALLS_WGD_COLUMN_INDEX]

  facets = {}
  # read in facets file and parse sample ids
  with open(facets_filename, 'r') as facets_file:
    facets_reader = csv.reader(facets_file, delimiter='\t')
    facets_header = facets_reader.next()

    if facets_header != expected_facets_columns:
      print >>sys.stderr, "ERROR: expected columns '%s' differ from actual columns '%s' in '%s'" % (", ".join(expected_facets_columns), ", ".join(facets_header), facets_filename)
      sys.exit(2)

    facets_header = facets_header[1:]
  
    for row in facets_reader:
      tumor_sample_id = row[0].split("__")[1].split(".")[0] # currently looks like this: s_C_006719_N001_d.Group0.rg.md.abra.printreads__s_C_006719_P001_d.Group0.rg.md.abra.printreads_hisens
      if tumor_sample_id in facets:
        print >>sys.stderr, "ERROR: sample id '%s' is duplicated in '%s', not sure what to do" % (tumor_sample_id, facets_filename)
        sys.exit(2)
      facets[tumor_sample_id] = row[1:]

  with open(portal_filename, 'r') as portal_file:
    portal_reader = csv.reader(portal_file, delimiter='\t')
    portal_header = portal_reader.next()
    writer = csv.writer(sys.stdout, delimiter='\t', lineterminator='\n')

    # this will clearly fail if column definition order ever changes
    while portal_header[0].startswith("#"):
      writer.writerow(portal_header + facets_column_definitions.pop(0))
      portal_header = portal_reader.next()
    
    if portal_header[0] != "SAMPLE_ID":
      print >>sys.stderr, "ERROR: expected column 'SAMPLE_ID' to be first column in '%s'" % (portal_filename)
      sys.exit(2)

    out_header = portal_header + [ "FACETS_VERSION" if h == "Facets" else "FACETS_%s" % (h.upper().replace(".", "_")) for h in facets_header] + ["FACETS_WGD"]
    writer.writerow(out_header)

    for row in portal_reader: 
      #sample_id = re.sub("^s_", "", row[0])
      sample_id = row[0]
      if sample_id not in sample_to_wgd:
        print >>sys.stderr, "ERROR: sample id '%s' was not found in '%s', are we supposed to carry on and fill in empty values?" % (sample_id, gene_calls_filename)
        sys.exit(2)
      elif sample_id not in facets:
        print >>sys.stderr, "ERROR: sample id '%s' was not found in '%s', are we supposed to carry on and fill in empty values?" % (sample_id, facets_filename)
        sys.exit(2)
      else:
        writer.writerow(row + facets[sample_id] + [sample_to_wgd[sample_id]])     
        del facets[sample_id]
        del sample_to_wgd[sample_id]

    if facets:
      print >>sys.stderr, "ERROR: sample ids: '%s' not found in '%s'" % (", ".join(facets.keys()), portal_filename)
      sys.exit(2)

    if sample_to_wgd:
      print >>sys.stderr, "ERROR: sample ids: '%s' not found in '%s'" % (", ".join(sample_to_wgd.keys()), gene_calls_filename)
      sys.exit(2)

def usage():
  print "python add_sample_atts.py --verbose --facets_filename Proj_[PROJECT_ID]___[TYPE]_OUT.txt --portal_filename data_clinical.txt --gene_calls_filename Proj_[PROJECT_ID]____[TYPE]_GeneCalls_v2.txt" 
  print "    e.g. /opt/common/CentOS_6/python/python-2.7.8/bin/python /home/wilson/FACETS/scripts/add_sample_atts.py  -f Proj_08390_OUT.txt -p /ifs/res/pi/Proj_08390.c881d62c-9e7a-11e8-859a-645106ef9e4c/portal/data_clinical_sample.txt -g Proj_08390___HISENS_GeneCalls_v2.txt > data_clinical_sample.txt"
  print "Where:"
  print "    -f facets_filename, required"
  print "    -p portal_filename, required"
  print "    -g gene_calls_filename, required"
  print "    -v for verbose logging (optional)"
  print "Writes an updated data_clinical_sample.txt file to stdout"

def main():
  try:
    opts, args = getopt.getopt(sys.argv[1:], "f:p:g:vh", ["facets_filename=", "portal_filename=", "gene_calls_filename=", "verbose", "help"])
  except getopt.GetoptError as err:
    # print help information and exit:
    print str(err) # will print something like "option -a not recognized"
    usage()
    sys.exit(2)

  verbose = False
  facets_filename = None
  portal_filename = None
  gene_calls_filename = None
  for o, a in opts:
    if o in ("-v", "--verbose"):
      verbose = True
    elif o in ("-f", "--facets_filename"):
      facets_filename = a
    elif o in ("-p", "--portal_filename"):
      portal_filename = a
    elif o in ("-g", "--gene_calls_filename"):
      gene_calls_filename = a
    elif o in ("-h", "--help"):
      usage()
      sys.exit(0)  
    else:
      assert False, "unhandled option '%s'" % (o)

  if not facets_filename or not os.path.isfile(facets_filename):
    print >>sys.stderr, "ERROR: facets_filename '%s' is required" % (facets_filename)
    usage()
    sys.exit(2)

  if not portal_filename or not os.path.isfile(portal_filename):
    print >>sys.stderr, "ERROR: portal_filename '%s' is required" % (portal_filename)
    usage()
    sys.exit(2)

  if not gene_calls_filename or not os.path.isfile(gene_calls_filename):
    print >>sys.stderr, "ERROR: gene_calls_filename '%s' is required" % (gene_calls_filename)
    usage()
    sys.exit(2)

  run(facets_filename, portal_filename, gene_calls_filename, verbose)

if __name__ == "__main__":
    main()
