#!/usr/bin/env python
# File created on 09 Feb 2010
#summarize_otu_by_cat.py
from __future__ import division

__author__ = "Julia Goodrich"
__copyright__ = "Copyright 2011, The QIIME Project"
__credits__ = ["Julia Goodrich"]
__license__ = "GPL"
__version__ = "1.2.1-dev"
__maintainer__ = "Daniel McDonald"
__email__ = "wasade@gmail.com"
__status__ = "Development"
 
from os import getcwd, makedirs
from qiime.util import parse_command_line_parameters
from optparse import make_option
from qiime.summarize_otu_by_cat import summarize_by_cat


script_info={}
script_info['brief_description']="""Summarize an OTU table by a single column in the mapping file."""
script_info['script_description']="""Collapse an OTU table based on values in a single column in the mapping file. For example, if you have 10 samples, five of which are from females and five of which are from males, you could use this script to collapse the ten samples into two corresponding based on their values in a 'Sex' column in your mapping file."""
script_info['script_usage']=[]
script_info['script_usage'].append(("""Example:""",""" Collapsed otu_table.txt on the 'Sex' column in map.txt and write the resulting OTU table to otu_table_by_sex.txt""","""summarize_otu_by_cat.py -c otu_table.txt -i map.txt -m Sex -o otu_table_by_sex.txt"""))
script_info['output_description']= """"""
script_info['required_options']=[\
make_option('-i', '--mapping_fp',
            help='path to mapping file [REQUIRED]'),
make_option('-c', '--otu_table_fp',
            help='path to otu table [REQUIRED]'),
make_option('-m', '--mapping_category',
            help='mapping category to collapse otu table on [REQUIRED]'),
make_option('-o', '--output_fp', dest='output_fp',
            help='path to store output file [REQUIRED]'),
]

script_info['optional_options']=[\
    make_option('-n', '--normalize',
         help='if True will normalize counts [default: %default]',
         default=False,
         action = 'store_true')
]

script_info["version"] = __version__

def main():
    option_parser, opts, args = parse_command_line_parameters(**script_info)
    
    mapping_fp = opts.mapping_fp
    mapping_category = opts.mapping_category
    normalize = opts.normalize
    otu_table_fp = opts.otu_table_fp
    output_fp = opts.output_fp
    
    mapping_f = open(mapping_fp,'U')
    otu_table_f = open(otu_table_fp,'U')

    summarized_otu_table = \
     summarize_by_cat(mapping_f,otu_table_f,mapping_category,normalize)
     
    f = open(output_fp,'w')
    f.write(summarized_otu_table)
    f.close()

if __name__ == "__main__":
    main()
