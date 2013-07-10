#!/usr/bin/env python
# File created on 19 Jun 2013
from __future__ import division

__author__ = "Greg Caporaso"
__copyright__ = "Copyright 2013, The QIIME project"
__credits__ = ["Greg Caporaso"]
__license__ = "GPL"
__version__ = "1.7.0-dev"
__maintainer__ = "Greg Caporaso"
__email__ = "gregcaporaso@gmail.com"
__status__ = "Development"

from os.path import join
from math import ceil
from numpy import median, mean
import matplotlib
from matplotlib.pyplot import subplots
from pylab import savefig
from cogent.util.misc import create_dir
from cogent.maths.stats.test import t_one_sample
from biom.parse import parse_biom_table
from qiime.parse import (extract_per_individual_state_metadata_from_mapping_f,
 extract_per_individual_state_metadata_from_mapping_f_and_biom)
from qiime.util import (parse_command_line_parameters, 
                  make_option)
from qiime.filter import (filter_mapping_file_from_mapping_f,
                          sample_ids_from_metadata_description)

script_info = {}
script_info['brief_description'] = "Generate plots which illustrate the change in some data point(s) with a state change on a per-individual basis."
script_info['script_description'] = ""
script_info['script_usage'] = []
script_info['script_usage'].append(("Generate plots for two categories from the mapping file.","","%prog -m map.txt --metadata_categories 'Streptococcus Abundance,Veillonella Abundance' --state_category TreatmentState --state_values Pre,Post --individual_id_category PersonalID -o taxa_results"))
script_info['script_usage'].append(("Generate plots for four categories from the mapping file, where the y-axes should be set on a per-plot basis.","","%prog -m map.txt --metadata_categories 'Streptococcus Abundance,Veillonella Abundance,Phylogenetic Diversity,Observed OTUs' --state_category TreatmentState --state_values Pre,Post --individual_id_category PersonalID -o taxa_and_alpha_results --suppress_share_y_axis"))
script_info['script_usage'].append(("Generate plots for all observations in a biom file, where the y-axes should be set on a per-plot basis.","","%prog -m map.txt -b otu_table.biom --state_category TreatmentState --state_values Pre,Post --individual_id_category PersonalID -o otu_results --suppress_share_y_axis"))
script_info['script_usage'].append(("Generate plots for all observations in a biom file, where the y-axes should be set on a per-plot basis, and only including samples from individuals whose 'TreatmentResponse' was 'Improved' (as defined in the mapping file).","","%prog -m map.txt -b otu_table.biom --state_category TreatmentState --state_values Pre,Post --individual_id_category PersonalID -o otu_results_improved_only --suppress_share_y_axis --valid_states TreatmentResponse:Improved"))

script_info['output_description']= ""

script_info['required_options'] = [
 make_option('-m','--mapping_fp',type="existing_filepath",help='the input filepath'),
 make_option('-o','--output_dir',type="new_filepath",help='directory where output files should be saved'),
 make_option('--state_category',help='the mapping file column name to plot change over (usually has values like "pre-treatment" and "post-treatment")'),
 make_option('--state_values',help='ordered list of state values to test change over (defines direction of graphs, generally something like "pre-treatment,post-treatment"). currently limited to two states.'),
 make_option('--individual_id_category',help='the mapping file column name containing each individual\'s identifier (usually something like "personal_identifier")'),
]

script_info['optional_options'] = [
 make_option('--suppress_share_y_axis',default=False,action='store_true',help='set the scale of the y-axes will be set on a per-plot basis, rather than made consistent across all subplots [default: %default]'),
  make_option('--metadata_categories',help='ordered list of the mapping file column names to test for paired differences (usually something like "StreptococcusAbundance,Phylogenetic Diversity") [default: %default]',default=None),
  make_option('--observation_ids',help='ordered list of the observation ids to test for paired differences if a biom table is provided (usually something like "otu1,otu2") [default: compute paired differences for all observation ids]',default=None),
  make_option('-b','--biom_table_fp',help='path to biom table to use for computing paired differences [default: %default]', default=None),
  make_option('-s','--valid_states', help="string describing valid samples that should be included based on their metadata (e.g. 'TreatmentResponse:Improved') [default: %default]",default=None),
]

script_info['version'] = __version__

def main():
    option_parser, opts, args =\
       parse_command_line_parameters(**script_info)
    
    mapping_fp = opts.mapping_fp
    state_values = opts.state_values.split(',')
    metadata_categories = opts.metadata_categories
    state_category = opts.state_category
    individual_id_category = opts.individual_id_category
    output_dir = opts.output_dir
    biom_table_fp = opts.biom_table_fp
    observation_ids = opts.observation_ids
    valid_states = opts.valid_states
    
    if metadata_categories and biom_table_fp:
        option_parser.error("Can only pass --metadata_categories or --biom_table_fp, not both.")
    elif not (metadata_categories or biom_table_fp):
        option_parser.error("Must pass either --metadata_categories or --biom_table_fp.")
    else:
        pass
    
    if len(state_values) != 2:
        option_parser.error("Exactly two state_values must be passed separated by a comma.")
    
    mapping_f = list(open(mapping_fp,'U'))
    if valid_states:
        sample_ids_to_keep = sample_ids_from_metadata_description(
                              mapping_f,valid_states)
        mapping_f = filter_mapping_file_from_mapping_f(mapping_f,sample_ids_to_keep).split('\n')
    
    if biom_table_fp:
        biom_table = parse_biom_table(open(biom_table_fp,'U'))
        metadata_categories = observation_ids or biom_table.ObservationIds
        personal_ids_to_state_metadata = \
         extract_per_individual_state_metadata_from_mapping_f_and_biom(
                                     mapping_f,
                                     biom_table,
                                     state_category,
                                     state_values,
                                     individual_id_category,
                                     observation_ids=metadata_categories)
    else:
        metadata_categories = metadata_categories.split(',')
        personal_ids_to_state_metadata = \
         extract_per_individual_state_metadata_from_mapping_f(
                                     mapping_f,
                                     state_category,
                                     state_values,
                                     individual_id_category,
                                     metadata_categories)
    
    num_cols = 3
    num_metadata_categories = len(metadata_categories)
    num_rows = int(ceil(num_metadata_categories / num_cols))
    num_unused_subplots = (num_rows * num_cols) - num_metadata_categories
    
    # create the subplot grid
    fig, splts = subplots(num_rows,
                        num_cols,
                        sharex=False,
                        sharey=not opts.suppress_share_y_axis)
    for i in range(num_cols,num_cols - num_unused_subplots,-1):
        # blank out un-used subplot spaces
        try:
            splts[-1][i-1].axis('off')
        except TypeError:
            splts[i-1].axis('off')
    x_values = range(len(state_values))
    
    create_dir(opts.output_dir)
    
    paired_difference_output_fp = join(opts.output_dir,'paired_difference_comparisons.txt')
    paired_difference_output_f = open(paired_difference_output_fp,'w')
    paired_difference_output_f.write("#Metadata category\tNum differences (i.e., n)\nMean difference\tMedian difference\tt one sample\tt one sample parametric p-value\tt one sample parametric p-value (Bonferroni-corrected)\n")
    paired_difference_results = []
    plot_output_fp = join(opts.output_dir,'plots.pdf')


    for category_number, metadata_category in enumerate(metadata_categories):
        personal_ids_to_state_metadatum = personal_ids_to_state_metadata[metadata_category]

        # identify the current subplot
        row_num = int(category_number/num_cols)
        col_num = int(category_number % num_cols)
        try:
            current_subplot = splts[row_num][col_num]
        except TypeError:
            # there is only one row, so the plot is 
            # access only by column number
            current_subplot = splts[col_num]
        
        # initialize a list to store the distribution of changes in metadata 
        # value with state change
        differences = []
        
        for pid, data in personal_ids_to_state_metadatum.items():
            if None in data:
                # if any of the data points are missing, skip this 
                # individual
                continue
            else:
                # otherwise compute the difference between the ending
                # and starting state
                differences.append(data[1] - data[0])
                # and plot the start and stop values as a line
                current_subplot.plot(x_values,
                                     data,
                                     "black",
                                     linewidth=0.5)
        
        # Compute stats for current metadata category
        t_one_sample_results = t_one_sample(differences)
        t = t_one_sample_results[0]
        p_value = t_one_sample_results[1]
        bonferroni_p_value = min([p_value * num_metadata_categories,1.0])
        paired_difference_results.append([metadata_category,
                                        len(differences),
                                        mean(differences),
                                        median(differences),
                                        t,
                                        p_value,
                                        bonferroni_p_value])
        
        # Finalize plot for current metadata category
        current_subplot.set_title(metadata_category,size=8)
        current_subplot.set_xticks(range(len(state_values)))
        current_subplot.set_xticklabels(state_values,size=6)
    
    fig.savefig(plot_output_fp)
    # sort output by absolute value of t (largest to smallest)
    paired_difference_results.sort(key=lambda x: abs(x[3]))
    paired_difference_results.reverse()
    for r in paired_difference_results:
        paired_difference_output_f.write('\t'.join(map(str,r)))
        paired_difference_output_f.write('\n')
    paired_difference_output_f.close()
        

if __name__ == "__main__":
    main()