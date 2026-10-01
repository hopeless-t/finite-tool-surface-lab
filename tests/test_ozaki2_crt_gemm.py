from __future__ import annotations

import unittest

from finite_tool_surface_lab.ozaki2_crt_gemm import (
    crt_centered,
    matmul_int,
    ozaki2_integer_core,
    residue_gemm,
)


class Ozaki2ToyTests(unittest.TestCase):
    def test_three_moduli_reconstruct_exact_integer_gemm(self):
        a=[[12,-7,3],[4,5,-9]]
        b=[[2,8],[-6,1],[7,-4]]
        result=ozaki2_integer_core(a,b,(127,125,121))
        self.assertTrue(result.uniqueness_condition_holds)
        self.assertTrue(result.exact_match)
        self.assertEqual(result.low_precision_gemm_count,3)
        self.assertEqual(result.reconstructed,matmul_int(a,b))

    def test_each_low_precision_gemm_matches_exact_product_modulus(self):
        a=[[10,-12],[7,3]]
        b=[[-4,5],[6,11]]
        exact=matmul_int(a,b)
        for p in (127,125,121):
            got=residue_gemm(a,b,p)
            want=[[x%p for x in row] for row in exact]
            self.assertEqual(got,want)

    def test_crt_centered_recovers_negative_integer(self):
        x=-321
        mods=(127,125,121)
        self.assertEqual(crt_centered((x%p for p in mods),mods),x)

    def test_insufficient_modulus_product_exposes_aliasing(self):
        a=[[20]]
        b=[[20]]
        result=ozaki2_integer_core(a,b,(5,7))
        self.assertFalse(result.uniqueness_condition_holds)
        self.assertFalse(result.exact_match)

    def test_non_coprime_moduli_fail(self):
        with self.assertRaisesRegex(ValueError,"pairwise_coprime"):
            ozaki2_integer_core([[1]],[[1]],(9,15))


if __name__=="__main__":
    unittest.main()
