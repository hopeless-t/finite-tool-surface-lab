from __future__ import annotations

import unittest

from finite_tool_surface_lab.dual_kitten_circuits import (
    demo_two_circuits,
    encode_coordinates,
    exact_coordinate_decode,
    majority_vote,
    redundant_coordinate_decode,
)


class DualKittenCircuitTests(unittest.TestCase):
    def test_vote_circuit_tolerates_two_of_five_wrong_votes(self):
        row=majority_vote((True,True,True,False,False))
        self.assertEqual(row.status,"DECIDED")
        self.assertTrue(row.decision)

    def test_vote_circuit_can_be_confidently_wrong_under_correlated_error(self):
        row=majority_vote((False,False,False,True,True))
        self.assertEqual(row.status,"DECIDED")
        self.assertFalse(row.decision)

    def test_exact_coordinate_circuit_reconstructs_latent_integer(self):
        x=321
        mods=(127,125,121)
        residues=encode_coordinates(x,mods)
        self.assertEqual(exact_coordinate_decode(residues,mods),x)

    def test_single_bad_coordinate_breaks_plain_crt(self):
        x=321
        mods=(127,125,121)
        residues=list(encode_coordinates(x,mods))
        residues[1]=(residues[1]+1)%mods[1]
        self.assertNotEqual(exact_coordinate_decode(residues,mods),x)

    def test_redundant_coordinate_circuit_corrects_one_bad_coordinate(self):
        x=321
        mods=(127,125,121,119)
        residues=list(encode_coordinates(x,mods))
        residues[1]=(residues[1]+1)%mods[1]
        row=redundant_coordinate_decode(
            residues,mods,legitimate_bound=1000,subset_size=3,minimum_support=3
        )
        self.assertEqual(row.status,"CORRECTED_OR_VERIFIED")
        self.assertEqual(row.value,x)
        self.assertEqual(row.support,3)

    def test_redundant_decoder_holds_when_too_many_coordinates_disagree(self):
        x=321
        mods=(127,125,121,119)
        residues=list(encode_coordinates(x,mods))
        residues[0]=(residues[0]+9)%mods[0]
        residues[1]=(residues[1]+11)%mods[1]
        row=redundant_coordinate_decode(
            residues,mods,legitimate_bound=1000,subset_size=3,minimum_support=3
        )
        self.assertNotEqual(row.status,"CORRECTED_OR_VERIFIED")
        self.assertIsNone(row.value)

    def test_demo_exposes_different_failure_topologies(self):
        row=demo_two_circuits()
        self.assertTrue(row.vote_value)
        self.assertEqual(row.coordinate_exact_value,321)
        self.assertNotEqual(row.coordinate_corrupt_value,321)
        self.assertEqual(row.redundant_value,321)


if __name__=="__main__":
    unittest.main()
