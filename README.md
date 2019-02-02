# DANCE - DAtabase of Nitrogen CEnters

<!-- toc -->

- [Usage](#usage)
  - [Example](#example)
    - [FILTER mode](#filter-mode)
    - [PLOTHIST mode](#plothist-mode)
    - [SELECT mode](#select-mode)
- [A Note on Logging](#a-note-on-logging)

<!-- tocstop -->

This tool filters molecules from a database. These molecules are then used to
generate parameters for smirnoff99frosst.

The heart of the tool is `dance.py`. It should be used as follows:

1. Use FILTER mode to select molecules with a single trivalent nitrogen from the
   database. The database must be represented as directories consisting of mol2
   files. When run in filter mode, FILTER mode ultimately generates the
   following files (which you may choose to rename when invoking `dance.py`):
   - `output-mols.smi`: holds SMILES strings representing the molecules
   - `output-tri-n-data.csv`: holds data about the trivalent nitrogen in each
     molecule - the total Wiberg bond order, total bond angle, and total bond
     length of the bonds surrounding the nitrogen
   - `output-tri-n-bonds.csv`: holds data about the individual bonds connected to
     the trivalent nitrogen - the Wiberg bond order, bond length, and element of
     each bond
2. Use PLOTHIST mode to visualize the Wiberg bond orders from the previous step.
   This requires the `output-tri-n-data.csv` file from the FILTER step. This
   step ultimately outputs the following file:
   - `output-histogram.pdf`: a PDF file holding histograms of the bond orders in
     every output-tri-n-data.csv file you pass in, as well as a histogram of the
     bond orders in all files combined (put on one plot together)
3. Use SELECT mode to make a final selection of molecules. This mode takes in
   all the molecules, sorts them again by Wiberg bond order, splits them into
   several bins, and selects the smallest molecules from each bin. This requires
   the `output-mols.smi` and `output-tri-n-data.csv` from the FILTER step.

*note: SELECT mode coming soon*

## Usage

Below is the help message for dance.py. Adding `python` before the
invocation of dance.py is optional.

```
usage: dance.py [-h] [--mode MODE] [--log LEVEL] [--mol2dirs DIR1,DIR2,...]
                [--output-mols FILENAME.smi]
                [--output-tri-n-data FILENAME.csv]
                [--output-tri-n-bonds FILENAME.csv]
                [--tri-n-data-csvs CSV1,CSV2,...]
                [--output-histograms FILENAME.pdf]

Performs various functions for selecting molecules from a database. It will do
the following based on the mode. FILTER - Take in directories of mol2 files,
filter out molecules with a single trivalent nitrogen, sort them by Wiberg
bond order, and write them to a file. PLOTHIST - Take in data files from the
previous step and use matplotlib to create histograms of the Wiberg bond
orders. SELECT - Make a final selection of molecules from the ones generated
in the first step. See README for more info.

optional arguments:
  -h, --help            show this help message and exit

Mode Agnostic args:
  Arguments which apply to every mode of DANCE

  --mode MODE           The mode in which to run DANCE - one of FILTER,
                        PLOTHIST, or SELECT. See README for more info
                        (default: FILTER)
  --log LEVEL           logging level - one of DEBUG, INFO, WARNING, ERROR,
                        and CRITICAL - See
                        https://docs.python.org/3/howto/logging.html for more
                        information (default: info)

FILTER args:
  --mol2dirs DIR1,DIR2,...
                        a comma-separated list of directories with mol2 files
                        to be filtered (default: )
  --output-mols FILENAME.smi
                        location of SMILES file holding final filtered
                        molecules (default: output-mols.smi)
  --output-tri-n-data FILENAME.csv
                        location of CSV file holding data about trivalent
                        nitrogens (with molecules in the same order as the
                        SMILES file (default: output-tri-n-data.csv)
  --output-tri-n-bonds FILENAME.csv
                        location of CSV file holding data about individual
                        bonds around trivalent nitrogens (default: output-tri-
                        n-bonds.csv)

PLOTHIST args:
  --tri-n-data-csvs CSV1,CSV2,...
                        a comma-separated list of CSV files, each of the same
                        form as the output-tri-n-data.csv generated in the
                        FILTER step (default: )
  --output-histograms FILENAME.pdf
                        location of PDF file for histograms (default: output-
                        histograms.pdf)
```

### Example

#### FILTER mode

```
dance.py --mode FILTER \
         --mol2dirs dir1,dir2,dir3 \
         --output-mols output-mols.smi \
         --output-tri-n-data output-tri-n-data.csv \
         --output-tri-n-bonds output-tri-n-bonds.csv \
         --log debug
```

Reads in molecules from dir1, dir2, and dir3, filters them, and writes the
resulting molecules to output-mols.smi. Additional data are stored in
output-tri-n-data.csv and output-tri-n-bonds.csv. Prints log messages as low as
DEBUG to stderr.

#### PLOTHIST mode

```
dance.py --mode PLOTHIST \
         --tri-n-data-csvs data1.csv,data2.csv,data3.csv \
         --output-histograms output-histograms.pdf \
         --log debug
```

Reads in Wiberg bond orders from data1.csv, data2.csv, and data3.csv and
generates histograms of the bond orders in each file. Also generates a histogram
for the bond orders from all files combined together. Writes the histograms to
output-histograms.pdf. Prints log messages as low as DEBUG to stderr.

#### SELECT mode

(Coming soon)

## A Note on Logging

Python's standard logging library is used to write log messages of varying
severity to stderr. The severity level required for a message to be printed can
be adjusted with the `--log` flag. To capture the messages in a file, you will
have to redirect stderr to a file. For example, the following command will
redirect stderr to a file called status.txt when running dance.py.

```
dance.py --mode FILTER --mol2dirs dir1,dir2,dir3 2> status.txt
```
