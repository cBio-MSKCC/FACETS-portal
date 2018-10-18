# FACETS-portal

Generates portal-ready files from FACETS and pipeline output.

## data_CNA.txt and data_ASCNA.txt

CWD: wilson@alpha:~/FACETS/Proj_08390
 
```
export PATH=.:/opt/common/CentOS_6-dev/bin/current/:$PATH
 
/opt/common/CentOS_6-dev/FACETS/1.5.6/facets geneLevel \
  -f /ifs/res/pi/Proj_08390.c881d62c-9e7a-11e8-859a-645106ef9e4c/facets/*_hisens.cncf.txt \
  -t /home/socci/Code/Pipelines/FACETS/GeneLevelIntervalFiles/FacetsIlists/IMPACT468_targets_FACETS.ilist \
  -o Proj_08390___HISENS_GeneCalls_v2.txt 
 
/opt/common/CentOS_6/python/python-2.7.8/bin/python /home/wilson/FACETS/scripts/split_gene_file.py \
  -g /home/wilson/FACETS/Proj_08390/Proj_08390___HISENS_GeneCalls_v2.txt \
  -p /ifs/res/pi/Proj_08390.c881d62c-9e7a-11e8-859a-645106ef9e4c/inputs/Proj_08390_sample_pairing.txt \
  -d /home/wilson/FACETS/Proj_08390/
``` 
 
NOTE: we previously stored more data in data_ASCNA.txt, to go back to this file format use this:
``` 
/opt/common/CentOS_6/python/python-2.7.8/bin/python /home/wilson/FACETS/scripts/split_gene_file.2018_10_15.py \
  -g /home/wilson/FACETS/Proj_08390/Proj_08390___HISENS_GeneCalls_v2.txt \
  -p /ifs/res/pi/Proj_08390.c881d62c-9e7a-11e8-859a-645106ef9e4c/inputs/Proj_08390_sample_pairing.txt \
  -d /home/wilson/FACETS/Proj_08390/
```

## data_mutations_extended.txt

CWD: wilson@alpha:~/FACETS/Proj_08390
 
```
export PATH=.:/opt/common/CentOS_6-dev/bin/current/:$PATH
``` 
Map MAF Tumor_Sample_Barcode values to FACETS Rdata files:
``` 
sh /home/wilson/FACETS/scripts/map_tumor_sample_barcode_to_rdata_file.sh \
  /ifs/res/pi/Proj_08390.c881d62c-9e7a-11e8-859a-645106ef9e4c/portal/data_mutations_extended.txt \
  /ifs/res/pi/Proj_08390.c881d62c-9e7a-11e8-859a-645106ef9e4c/facets/ > facets_mapping.txt
``` 
Now annotate MAF:
``` 
/opt/common/CentOS_6-dev/FACETS/1.5.6/facets mafAnno -c \
  -m /ifs/res/pi/Proj_08390.c881d62c-9e7a-11e8-859a-645106ef9e4c/portal/data_mutations_extended.txt \
  -f facets_mapping.txt \
  -o data_mutations_extended.txt 
```

## \*_data_cna_hg19.seg

CWD: wilson@alpha:~/FACETS/Proj_08390
 
```
export PATH=.:/opt/common/CentOS_6-dev/bin/current/:$PATH
 
/opt/common/CentOS_6-dev/FACETS/1.5.6/summarize_project.py \
  -s /ifs/res/pi/Proj_08390.c881d62c-9e7a-11e8-859a-645106ef9e4c/facets/*_hisens.seg \
  -c /ifs/res/pi/Proj_08390.c881d62c-9e7a-11e8-859a-645106ef9e4c/facets/*_hisens.cncf.txt \
  -o /ifs/res/pi/Proj_08390.c881d62c-9e7a-11e8-859a-645106ef9e4c/facets/*_hisens.out
```
 
Note: The output FACETS produces per sample is the \*cncf.txt file and a the \*.seg (plus some other). The former contains basically all the data from the copy-number segmentation, the latter is a simplified IGV-style representation of this. The "cnlr.median" and "seg.mean" fields should be equivalent, the different naming is only to allow for IGV to read the \*.seg files.

## data_clinical_sample.txt

CWD: wilson@alpha:~/FACETS/Proj_08390

```
/opt/common/CentOS_6/python/python-2.7.8/bin/python /home/wilson/FACETS/scripts/add_sample_atts.py \
  -f Proj_08390_OUT.txt \
  -p /ifs/res/pi/Proj_08390.c881d62c-9e7a-11e8-859a-645106ef9e4c/portal/data_clinical_sample.txt \
  -g Proj_08390___HISENS_GeneCalls_v2.txt > data_clinical_sample.txt
```

## Setting up portal study

CWD: wilson@alpha:~/FACETS/Proj_08390

```
cp data_clinical_sample.txt ~/merges/bic-mskcc/test/mskcc/wilson/08390
cp data_ASCNA_facets.txt ~/merges/bic-mskcc/test/mskcc/wilson/08390/data_ASCNA.txt
cp data_CNA_facets.txt ~/merges/bic-mskcc/test/mskcc/wilson/08390/data_CNA.txt
cp data_mutations_extended.txt ~/merges/bic-mskcc/test/mskcc/wilson/08390
cp Proj_08390_CNCF.txt ~/merges/bic-mskcc/test/mskcc/wilson/08390/test_mskcc_wilson_08390_data_cna_hg19.seg
```

Copied from pipelines directory:
* case_lists
* data_clinical_patient.txt
* meta_\*.txt
* test_mskcc_wilson_08390_meta_cna_hg19_seg.txt (SEG meta file)

TODO Manual modifications were made to all meta_\*.txt files and the SEG meta file.  This must be automated.
