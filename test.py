#!/usr/bin/env python

import argparse
import logging as lg
import pandas as pd
import subprocess
import sys


if __name__ == "__main__":
    ### define logger
    logger = lg.getLogger('Process_samples')
    logger.setLevel(lg.INFO)
    
    stdout_handler = lg.StreamHandler(sys.stdout)
    stdout_handler.setLevel(lg.INFO)
    logger.addHandler(stdout_handler)
    
    ### define arguments 
    parser = argparse.ArgumentParser(prog = 'Process_samples', description = 'Process and assembly metagenomic data brom burcera samples')
    parser.add_argument('-s', '--samples_file') ### input txt file with samples list
    # parser.add_argument('-v', '--threshold_val', default=0.95) ### minimum similitude value to keep a hit
    # parser.add_argument('-o', '--out_file') ### start date to process in format
    args = parser.parse_args()
    
    