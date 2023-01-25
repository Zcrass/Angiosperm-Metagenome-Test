# Methods to test the metagenome of Bursera species

## Prerequisites
This analysis was performed in a miniconda environment with the following software and its depencencies:

- spades 3.15.5
- getorganelle 1.7.6.1
- bwa 0.7.17
- samtools 1.6

NOTE: most of the software is listed in the conda_env.txt file and can be installed trough conda

All the software was runned in and Ubuntu distro under the Windows Subsystem For Linux 2 (WSL2) platform.
## Organelle assembly
Previous tests showed that some fragments of the chloroplast and mitochondria can be found across the reads so we have to remove those to obtain better results in our assemblies.

For this we used getorganelle as shown bellow:

```
mkdir assemblies blast_hits chloroplast raw_samples ref_gen sam 
while read f;
    do echo "assembly sample"; echo $f ; echo "###########################################################################";
    get_organelle_from_reads.py -1 raw_samples/$f'.R1.fastq.gz' -2 raw_samples/$f'.R2.fastq.gz' -t 8 -o mitochondria/$f -R 30 -k 21,45,65,85,105 -F embplant_mt --reduce-reads-for-coverage inf --max-reads inf;
    get_organelle_from_reads.py -1 raw_samples/$f'.R1.fastq.gz' -2 raw_samples/$f'.R2.fastq.gz' -t 8 -o chloroplast/$f -R 30 -k 21,45,65,85,105 -F embplant_pt --reduce-reads-for-coverage inf --max-reads inf;
done < samples_selected.txt

```
We manually edit resulting scaffold files to avoid duplicated scaffold names and save the edited files in the folder chloroplast and mitochondria respectivelly.

Then we concatenate the trhee genomes and index the resulting genome.
```
cat ref_gen/b_cuneata_ref_gen.fna mitochondria/*.fasta chloroplast/*.fasta > ref_gen/combined_genomes.fasta

bwa index ref_gen/combined_genomes.fasta
```

## Alingment and separation of unmapped reads
Then we aling each of the raw samples to the combined reference genome using bwa.
Then we used these files to extract the raw reads that does not map to the reference genome and store it as fastq files using samtools fastq.

```
while read f; do bwa mem -t 8 ref_gen/combined_genomes.fasta raw_samples/$f'.R1.fastq.gz' raw_samples/$f'.R2.fastq.gz' > sam/$f'_aligned.sam'; done < samples.txt

<!-- while read f; do echo sample $f; samtools view -S -b sam/$f'_aligned.sam' -o bam/$f'_aligned.bam'; done < samples.txt -->

while read f; do echo sample $f; samtools fastq -f 13 sam/$f'_aligned.sam' -1 unmapped/$f'.R1.unmapped.fastq' -2 unmapped/$f'.R2.unmapped.fastq'; done < samples.txt

```

Finally we assembly all samples in individual folders using spades.
```
while read f; do mkdir assemblies/$f; done < samples.txt

while read f; do spades.py -t 8 -1 unmapped/$f'.R1.unmapped.fastq' -2 unmapped/$f'.R2.unmapped.fastq' -o assemblies/$f; done < samples.txt

```
## Blasting the results
Then we can submit the resulting fasta files to BLAST in the NCBI platform.

First we renamed the resulting sccaffols
```
while read f; do cp 'assemblies/'$f'/scaffolds.fasta' assemblies/$f'_scaffolds.fasta'; done < samples.txt
```
And uploade it to blastn server. There we going to perform a search along the XXXX database as shown in the image bellow.

![BLAST search page](/assets/images/BLAST_%20Search.png)


After some time the resulting page is showed and we going to download all the results using the hit table in txt format.

![BLAST results page](/assets/images/BLAST_Results.png)


Then we can use the read_blasthits.py program to process the hit table and obtain a list of the organism that were found by blast as the most similar to the assembled sequences that we generated.

```
while read f; do ./read_blasthits.py -i blast_hits/$f'.txt' -o blast_hits/$f'_res.csv'; done < samples.txt
```




