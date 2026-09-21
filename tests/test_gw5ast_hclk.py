import unittest
from types import SimpleNamespace

from apycula import chipdb, wirenames


class GW5ASTHclkTests(unittest.TestCase):
    def setUp(self):
        chipdb.wire2node.clear()
        wirenames.select_wires('GW5AST-138C')

    def tearDown(self):
        chipdb.wire2node.clear()

    def test_six_blocks_use_gw5ast_divider_wire_numbers(self):
        for hclk in range(6):
            base = hclk * 187
            for lane in range(4):
                self.assertEqual(wirenames.hclknames[base + 110 + lane],
                                 f'CLKDIV_I{hclk}{lane}')
                self.assertEqual(wirenames.hclknames[base + 114 + lane],
                                 f'CLKDIV_O{hclk}{lane}')
                self.assertEqual(wirenames.hclknames[base + 118 + lane],
                                 f'HCLK{hclk}{lane}')

    def test_all_24_clkdiv_bels_are_created(self):
        dev = SimpleNamespace(
            extra_func={}, hclk_div2={}, hclk_pips={}, nodes={}, wire_delay={}
        )
        chipdb.gw5_add_hclk_bels(None, dev, 'GW5AST-138C')

        self.assertEqual(set(dev.hclk_div2), set(range(6)))
        self.assertEqual(sum(len(v) for v in dev.hclk_div2.values()), 24)
        for hclk, loc in chipdb._gw5a_hclk_locs['GW5AST-138C'].items():
            self.assertEqual(dev.extra_func[loc]['clkdiv']['hclk_idx'], hclk)
            self.assertEqual(len(dev.extra_func[loc]['clkdiv']['bels']), 4)

    def test_all_four_edges_expose_iologic_hclk_paths(self):
        dev = SimpleNamespace(rows=109, cols=182)
        for row, col in ((0, 40), (108, 40), (40, 0), (40, 181)):
            self.assertTrue(chipdb.gw5_create_hclk_iol_pip(
                dev, 'GW5AST-138C', row, col))
        self.assertFalse(chipdb.gw5_create_hclk_iol_pip(
            dev, 'GW5AST-138C', 40, 40))

    def test_device_enables_gw5_hclk_architecture(self):
        dev = SimpleNamespace(chip_flags=[], dcs_prefix=None)
        chipdb.set_chip_flags(dev, 'GW5AST-138C')
        self.assertIn('HAS_5A_HCLK', dev.chip_flags)


if __name__ == '__main__':
    unittest.main()
