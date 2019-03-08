"""Provides a class for selecting a final set of molecules."""

from collections import defaultdict
import math
import logging
import numpy as np
from openeye import oechem
from dance import danceprops
from dance import dancerunbase


class DanceSelector(dancerunbase.DanceRunBase):
    """
    Selects molecules, typically from the set generated by DanceGenerator.
    Separates molecules on the basis of:
        - total Wiberg bond order around the nitrogen atom
        - "fingerprint" around the nitrogen atom - see
          danceprops.DanceFingerprint
    Then, molecules are sorted by size in each bin, and the smallest are
    selected.

    Attributes:
        _mols: a list storing the molecules the class is currently handling
        _properties: a list storing properties of the _mols (see
                     danceprops for more info)
        _bin_size: size of bins for separating by Wiberg bond order
        _bins: a defaultdict mapping tuples of (Wiberg bond order bin,
               fingerprint) to a list of molecules; for bond order, bins are
               identified by their lower bound; e.g. with _bin_size of 0.02,
               having a bin of 3.00 means the nitrogen has a total bond order in
               the range [3.00, 3.02)
        _wiberg_precision: value to which to round the Wiberg bond orders in
                           the fingerprint
        _bin_select: how many molecules to select from each bin
    """

    #
    # Public
    #

    def __init__(self, mols: [oechem.OEMol],
                 properties: [danceprops.DanceProperties], bin_size: float,
                 wiberg_precision: float, bin_select: int):
        super().__init__()
        self._mols = mols
        self._properties = properties
        self._bin_size = bin_size
        self._bins = defaultdict(list)
        self._wiberg_precision = wiberg_precision
        self._bin_select = bin_select

    def run(self):
        """Performs all the molecule selection"""
        super().check_run_fatal()
        logging.info("STARTING SELECTING")
        self._add_fingerprints()
        self._separate_into_bins()
        self._select_by_size()
        logging.info("FINISHED SELECTING")

    def get_data(self) -> ([oechem.OEMol], [danceprops.DanceProperties]):
        """Return the molecules and properties associated with this class."""
        return self._mols, self._properties

    #
    # Private
    #

    def _add_fingerprints(self):
        """Adds fingerprints to all of the molecules"""
        for mol in self._mols:
            if not self._is_valid_molecule(mol):
                logging.debug(f"Ignored molecule {mol.GetTitle()}")
                continue
            charged_copy = mol.GetData(danceprops.DANCE_CHARGED_COPY_KEY)
            tri_n = None
            for atom in charged_copy.GetAtoms(oechem.OEIsInvertibleNitrogen()):
                tri_n = atom
                break
            danceprops.get_dance_property(
                mol,
                self._properties).fingerprint = danceprops.DanceFingerprint(
                    tri_n, self._wiberg_precision)
            logging.debug(f"Added fingerprint to {mol.GetTitle()}")

    def _separate_into_bins(self):
        """
        Separates the molecules into bins by Wiberg bond order; within each bin,
        molecules are further separated by fingerprints.
        """
        for mol in self._mols:
            if not self._is_valid_molecule(mol): continue

            # Retrieve the total bond order around the trivalent nitrogen
            bond_order = danceprops.get_dance_property(
                mol, self._properties).tri_n_bond_order

            # Round the total bond order down to the lowest multiple of
            # bin_size. For instance, if bin_size is 0.02, and the bond_order is
            # 2.028, it becomes 2.02. This works because
            # (bond_order / self._bin_size) generates a multiple of the
            # bin_size. Then floor() finds the next integer less than the
            # multiple. Finally, multiplying back by bin_size obtains the
            # nearest actual value.
            bond_order = math.floor(
                bond_order / self._bin_size) * self._bin_size

            # Retrieve the fingerprint for the molecule
            fingerprint = danceprops.get_dance_property(
                mol, self._properties).fingerprint

            # Select the bin for the molecule
            self._bins[bond_order, fingerprint].append(mol)

        logging.debug(f"Separated molecules into bins:")
        sorted_bins = sorted(self._bins.keys())
        for bin_id in sorted_bins:
            logging.debug(
                f"({bin_id[0]}, {bin_id[1]}) -> {len(self._bins[bin_id])} mols")

    def _select_by_size(self):
        """Selects the self._bin_select smallest molecules from each bin."""
        selected = []
        for b in self._bins:
            self._bins[b].sort(key=lambda mol: mol.NumAtoms())
            selected.extend(self._bins[b][:self._bin_select])
        self._mols = selected

        # Only retain properties of the selected molecules
        danceprops.clean_properties_list(self._mols, self._properties)

    @staticmethod
    def _is_valid_molecule(mol: oechem.OEMol) -> bool:
        """
        Some of the molecules coming into the DanceSelector may not be valid.
        DanceGenerator may find there was an error in charge calculations, in
        which case the charged copy was not assigned to the molecule. This
        function checks for that.
        """
        return mol.HasData(danceprops.DANCE_CHARGED_COPY_KEY)
