#!/bin/bash
# sh map_tumor_sample_barcode_to_rdata_file.sh /ifs/res/pi/Proj_08390.c881d62c-9e7a-11e8-859a-645106ef9e4c/portal/data_mutations_extended.txt /ifs/res/pi/Proj_08390.c881d62c-9e7a-11e8-859a-645106ef9e4c/facets/

if [ -z "$1" ]; then
  >&2 echo "MAF filename is required"
  exit 1
fi
maf=$1

if [ -z "$2" ]; then
  >&2 echo "Rdata file directory is required"
  exit 1
fi
rdata_dir=$2
if [ ! -d "$rdata_dir" ]; then
  >&2 echo "Rdata file directory '$rdata_dir' is not a directory"
  exit 1
fi

tumor_samples=`cut -f 16 $maf | grep -v Tumor_Sample_Barcode| grep -v "^#"| sort | uniq`

echo -e "Tumor_Sample_Barcode\tRdata_filename"
for tumor_sample in $tumor_samples; do
  tumor_sample_rdata_filename=`find $rdata_dir -name "*$tumor_sample*_hisens.Rdata"`
  if [ ! -f "$tumor_sample_rdata_filename" ]; then
    >&2 echo "Rdata file not found for '$tumor_sample', skipping"
  else
    echo -e "$tumor_sample\t$tumor_sample_rdata_filename"
  fi
done
