# DANCE - DAtabase of Nitrogen CEnters

<!-- toc -->

- [Dependencies](#dependencies)
- [Usage](#usage)
  - [Example](#example)
    - [GENERATE mode](#generate-mode)
    - [PLOTHIST mode](#plothist-mode)
    - [SELECT mode](#select-mode)
- [A Note on Logging](#a-note-on-logging)

<!-- tocstop -->

This tool filters molecules from a database. These molecules are then used to
generate parameters for smirnoff99frosst.

The heart of the tool is `dance.py`. It should be used as follows:

1. Use GENERATE mode to generate an initial set of trivalent nitrogen molecules
   from the database. The database must be represented as directories consisting
   of mol2 files. GENERATE mode ultimately generates the following files (which
   you may choose to rename when invoking `dance.py`):
   - `output-mols.smi`: SMILES strings representing the molecules
   - `output-mols.oeb`: an OEB (Openeye Binary) file for raw molecule data from
     DanceGenerator
   - `output-tri-n-data.csv`: holds data about the trivalent nitrogen in each
     molecule - the total Wiberg bond order, total bond angle, and total bond
     length of the bonds surrounding the nitrogen
   - `output-tri-n-bonds.csv`: holds data about the individual bonds connected
     to the trivalent nitrogen - the Wiberg bond order, bond length, and element
     of each bond
   - `dance-props.binary`: binary file for storing list of DanceProperties with
     data about the molecules
2. Use PLOTHIST mode to visualize the Wiberg bond orders from the previous step.
   This requires either the `output-tri-n-data.csv` file or the
   `output-tri-n-bonds.csv` from the GENERATE step. Note that if you choose the
   `output-tri-n-bonds.csv` file, you will have to change some of the command
   line arguments, as the defaults are for `output-tri-n-data.csv`.
   Specifically, `hist-min`, `hist-max`, and `hist-step` should be adjusted,
   most likely to around 0.5, 1.5, and 0.1, respectively. This step ultimately
   outputs the following file:
   - `output-histogram.pdf`: a PDF file holding histograms of the bond orders in
     every output-tri-n-data.csv file you pass in, as well as a histogram of the
     bond orders in all files combined (put on one plot together)
3. Use SELECT mode to make a final selection of molecules. This mode takes in
   all the molecules, sorts them again by Wiberg bond order, splits them into
   several bins, and selects the smallest molecules from each bin. This requires
   the `output-mols.smi` and `output-tri-n-data.csv` from the GENERATE step.

_note: SELECT mode coming soon_

## Dependencies

DANCE requires the following libraries to operate:

- Python standard library
- Openeye
- Matplotlib
- Numpy

## Usage

Below is the help message for dance.py. Adding `python` before the
invocation of dance.py is optional.

```
usage: dance.py [-h] [--mode MODE] [--log LEVEL] [--mol2dirs DIR1,DIR2,...]
                [--output-mols-smi FILENAME.smi]
                [--output-mols-oeb FILENAME.oeb]
                [--output-tri-n-data FILENAME.csv]
                [--output-tri-n-bonds FILENAME.csv]
                [--output-props-binary FILENAME.binary]
                [--wiberg-csvs CSV1,CSV2,...] [--wiberg-csv-col INT]
                [--output-histograms FILENAME.pdf] [--hist-min FLOAT]
                [--hist-max FLOAT] [--hist-step FLOAT]

Performs various functions for selecting molecules from a database. It will do
the following based on the mode. GENERATE - Take in directories of mol2 files,
generate the initial set of molecules with a single trivalent nitrogen, and
write the molecules and accompanying data to various files. PLOTHIST - Take in
data files from the previous step and use matplotlib to generate histograms of
the Wiberg bond orders. SELECT - Make a final selection of molecules from the
ones generated in the first step. See README for more info.

optional arguments:
  -h, --help            show this help message and exit

Mode Agnostic args:
  Arguments which apply to every mode of DANCE

  --mode MODE           The mode in which to run DANCE - one of GENERATE,
                        PLOTHIST, or SELECT. See README for more info
                        (default: GENERATE)
  --log LEVEL           logging level - one of DEBUG, INFO, WARNING, ERROR,
                        and CRITICAL - See
                        https://docs.python.org/3/howto/logging.html for more
                        information (default: info)

GENERATE args:
  --mol2dirs DIR1,DIR2,...
                        a comma-separated list of directories with mol2 files
                        to be filtered and saved (default: )
  --output-mols-smi FILENAME.smi
                        location of SMILES file holding final generated
                        molecules (default: output-mols.smi)
  --output-mols-oeb FILENAME.oeb
                        location of OEB (Openeye Binary) file holding final
                        molecules (default: output-mols.oeb)
  --output-tri-n-data FILENAME.csv
                        location of CSV file holding data about trivalent
                        nitrogens (with molecules in the same order as the
                        SMILES file (default: output-tri-n-data.csv)
  --output-tri-n-bonds FILENAME.csv
                        location of CSV file holding data about individual
                        bonds around trivalent nitrogens (default: output-tri-
                        n-bonds.csv)
  --output-props-binary FILENAME.binary
                        location of binary file holding DanceProperties
                        objects with data about the molecules (default:
                        output-props.binary)

PLOTHIST args:
  --wiberg-csvs CSV1,CSV2,...
                        a comma-separated list of CSV files with a column
                        containing wiberg bond orders - these files are likely
                        generated in the GENERATE step (default: )
  --wiberg-csv-col INT  Column in the CSV files holding the Wiberg bond orders
                        (0-indexed) (default: 0)
  --output-histograms FILENAME.pdf
                        location of PDF file for histograms (default: output-
                        histograms.pdf)
  --hist-min FLOAT      Minimum bin for histogram (default: 2.0)
  --hist-max FLOAT      Maximum bin for histogram (default: 3.4)
  --hist-step FLOAT     Step/bin size for histogram (default: 0.1)
```

### Example

#### GENERATE mode

```
dance.py --mode GENERATE \
         --mol2dirs dir1,dir2,dir3 \
         --output-mols-smi output-mols.smi \
         --output-mols-oeb output-mols.oeb \
         --output-tri-n-data output-tri-n-data.csv \
         --output-tri-n-bonds output-tri-n-bonds.csv \
         --output-props-binary output-props.binary \
         --log debug
```

Reads in molecules from dir1, dir2, and dir3, filters out the ones with a single
trivalent nitrogen atom, and writes the resulting molecules to output-mols.smi
and output-mols.oeb.  Additional data are stored in output-tri-n-data.csv and
output-tri-n-bonds.csv, and DanceProperties are stored in output-props.binary.
Prints log messages as low as DEBUG to stderr.

#### PLOTHIST mode

```
dance.py --mode PLOTHIST \
         --wiberg-csvs data1.csv,data2.csv,data3.csv \
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
dance.py --mode GENERATE --mol2dirs dir1,dir2,dir3 2> status.txt
```
