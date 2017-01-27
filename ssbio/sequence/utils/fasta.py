import ssbio.utils
import tempfile
import os.path as op
from Bio import SeqIO
from Bio import Alphabet
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.Alphabet import IUPAC


def write_fasta_file(seq_records, outname, outdir=None, outext='.faa', force_rerun=False):
    if not outdir:
        outdir = ''
    outfile = ssbio.utils.outfile_maker(inname='', outname=outname, outdir=outdir, outext=outext)

    if ssbio.utils.force_rerun(flag=force_rerun, outfile=outfile):
        SeqIO.write(seq_records, outfile, "fasta")

    return outfile


def write_fasta_file_from_dict(indict, outname, outdir=None, outext='.faa', force_rerun=False, ignore_alphabet=False):
    """Write a FASTA file for a dictionary of IDs and their sequence strings.

    Args:
        indict: Input dictionary with keys as IDs and values as sequence strings
        outname: Name of the output file which will have outext appended to it
        outdir: Path to directory to output sequences to
        outext: Extension of FASTA file, default ".faa"
        force_rerun: If file should be overwritten if it exists
        ignore_alphabet: Check the sequence to see if it contains valid characters

    Returns:
        str: Path to output FASTA file.

    """

    if not outdir:
        outdir = ''
    outfile = ssbio.utils.outfile_maker(inname='', outname=outname, outdir=outdir, outext=outext)

    if ssbio.utils.force_rerun(flag=force_rerun, outfile=outfile):
        seqs = []
        for i, s in indict.items():
            seq = load_seq_string_as_seqrecord(s, ident=i, ignore_alphabet=ignore_alphabet)
            seqs.append(seq)
        SeqIO.write(seqs, outfile, "fasta")

    return outfile


def load_seq_string_as_seqrecord(seq_str, ident, name='', desc='', ignore_alphabet=False):
    """Load an amino acid sequence string as a SeqRecord object

    Args:
        seq_str (str): A protein amino acid sequence
        ident (str): Database identifier (ie. UniProt or PDB ID)
        name (str): OPTIONAL protein name (ie. gene name)
        desc (str): OPTIONAL description of this sequence (ie. catabolizes G6P)
        ignore_alphabet (boolean): OPTIONAL check the alphabet to see if it contains valid amino acids.

    Returns:
        SeqRecord: Biopython SeqRecord object

    """

    my_seq = Seq(seq_str, Alphabet.IUPAC.extended_protein)

    if not Alphabet._verify_alphabet(my_seq) and not ignore_alphabet:
        raise ValueError('Sequence contains invalid characters')

    if not desc:
        desc = 'Loaded by ssbio on {}'.format(ssbio.utils.todays_long_date())

    my_seq_record = SeqRecord(my_seq, id=ident, name=name, description=desc)

    return my_seq_record


def load_seq_str_as_tempfasta(seq_str):
    sr = load_seq_string_as_seqrecord(seq_str, ident='tempfasta')
    return write_fasta_file(seq_records=sr, outname='temp', outdir=tempfile.gettempdir(), force_rerun=True)


def load_fasta_file(filename):
    """Load a FASTA file and return the sequences as a list of SeqRecords

    Args:
        filename (str): Path to the FASTA file to load

    Returns:
        list: list of all sequences in the FASTA file as Biopython SeqRecord objects

    """

    with open(filename, "r") as handle:
        records = list(SeqIO.parse(handle, "fasta"))
    return records


def load_fasta_file_as_dict_of_seqs(filename):
    """Load a FASTA file and return the sequences as a dict of {ID: sequence string}

    Args:
        filename (str): Path to the FASTA file to load

    Returns:
        dict: Dictionary of IDs to their sequence strings

    """

    results = {}
    records = load_fasta_file(filename)
    for r in records:
        results[r.id] = str(r.seq)

    return results


def fasta_files_equal(seq_file1, seq_file2):
    """Check equality of a FASTA file to another FASTA file

    Args:
        seq_file1: Path to a FASTA file
        seq_file2: Path to another FASTA file

    Returns:
        bool: If the sequences are the same

    """

    # Load already set representative sequence
    seq1 = SeqIO.read(open(seq_file1), 'fasta')

    # Load kegg sequence
    seq2 = SeqIO.read(open(seq_file2), 'fasta')

    # Test equality
    if str(seq1.seq) == str(seq2.seq):
        return True
    else:
        return False