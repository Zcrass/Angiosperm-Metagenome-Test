#!/usr/bin/env python

import argparse
import logging as lg
import pandas as pd
import subprocess
import sys


if __name__ == '__main__':
    ### define logger
    logger = lg.getLogger('readBlastHits')
    logger.setLevel(lg.INFO)
    
    stdout_handler = lg.StreamHandler(sys.stdout)
    stdout_handler.setLevel(lg.INFO)
    logger.addHandler(stdout_handler)
    
    ### define arguments 
    parser = argparse.ArgumentParser(prog = 'read_blasthits', description = 'Read a hit table in txt format and search in the NCBI database to obtain recover the unique species names from each sample')
    parser.add_argument('-i', '--input_table') ### input blast hit table in txt format
    parser.add_argument('-v', '--threshold_val', default=0.95) ### minimum similitude value to keep a hit
    parser.add_argument('-o', '--out_file') ### start date to process in format
    args = parser.parse_args()
           
    ### read hit table from blast resutls
    logger.info(f'Reading blast hits table...')
    hit_table = pd.read_table(args.input_table, comment='#')
    hit_table.columns = ['query_acc_ver', 'subject_acc_ver', 'pct_identity',
                        'alignment_length', 'mismatches', 'gap_opens',
                        ' q_start', 'q_end', 's_start', 's_end', 
                        'evalue', 'bit_score']
    logger.info(f'{hit_table.shape[1]} contigs read')

    ### extract the best hits for each contig
    hits = []
    # contig_list = []
    for contig in hit_table.query_acc_ver.unique():
        hits = hits + list(hit_table.loc[(hit_table.query_acc_ver == contig) & (hit_table.pct_identity > args.threshold_val), 'subject_acc_ver'])
        # contig_list = contig_list + [contig]
        
    ### keep only unique hits
    hits = list(set(hits))
    logger.info(f'Found {len(hits)} unique hits')

    ### search each accesion in NCBI GenBank to obtain the organism name
    organisms = []
    source = []
    accesion = []
    for c, acc in enumerate(hits):    
        org = 'NA'
        src = 'NA'
        logger.info(f'searching accesion:  {str(c + 1)}/{str(len(hits))}') 
        logger.info(f'command: efetch -db nuccore -id {acc} -format gb')
        gb_acc = subprocess.run(['efetch', '-db', 'nuccore', '-id', acc, '-format', 'gb'], stdout=subprocess.PIPE).stdout.decode('utf-8')
        
        for line in gb_acc.splitlines():
            if 'ORGANISM' in line:
                org = line.replace('ORGANISM', '').lstrip()
                
            if 'SOURCE' in line:
                src = line.replace('SOURCE', '').lstrip()
        accesion = accesion + [acc]
        organisms = organisms + [org]
        source = source + [src]
        logger.info(f'{org} - {src} - {acc}')
        # contig_list2 = contig_list2 + [contig_list[c]]

    ### save as dataframe
    # results = pd.DataFrame(data={'Accesion':hits, 'Organism':organisms, 'Source':source}).drop_duplicates().to_csv(args.out_file, index=False)
    # pd.DataFrame(data={'Scaffold': contig_list2, 'Accesion':accesion, 'Organism':organisms, 'Source':source}).drop_duplicates().to_csv(args.out_file, index=False)
    pd.DataFrame(data={'Accesion':accesion, 'Organism':organisms, 'Source':source}).drop_duplicates().to_csv(args.out_file, index=False)
    # results.to_csv(args.out_file, index=False)
