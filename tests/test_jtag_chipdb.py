import unittest
from types import SimpleNamespace

from apycula import chipdb, wirenames


class JtagChipdbTests(unittest.TestCase):
    def setUp(self):
        chipdb.wire2node.clear()

    def tearDown(self):
        chipdb.wire2node.clear()

    @staticmethod
    def make_dat(inputs, outputs):
        return SimpleNamespace(compat_dict={
            'JtagIns': inputs,
            'JtagOuts': outputs,
        })

    def test_gw5ast_uses_dat_inputs_and_left_neighbor_outputs(self):
        wirenames.select_wires('GW5AST-138C')
        dev = SimpleNamespace(extra_func={}, nodes={})
        dat = self.make_dat(
            [-1, -1, -1, 9, 13],
            [-1, 46, 45, 43, 44, 39, 38, -1, 42, 40, 41],
        )

        chipdb.fse_create_jtag(dev, 'GW5AST-138C', dat)

        jtag = dev.extra_func[(108, 166)]['jtag']
        self.assertEqual(jtag['inputs']['tdo_er1_i'], 'B2')
        self.assertEqual(jtag['inputs']['tdo_er2_i'], 'B3')
        self.assertEqual(jtag['outputs']['pause_dr_o'],
                         'DUMMY_JTAG_PAUSE_DR_O')
        self.assertEqual(jtag['outputs']['tck_o'], 'GW_JTAGtck_oQ6')
        self.assertEqual(
            dev.nodes['X166Y108/GW_JTAGtck_oQ6'][1],
            {(108, 166, 'GW_JTAGtck_oQ6'), (108, 165, 'Q6')},
        )

    def test_gw2a_keeps_local_jtag_wires(self):
        wirenames.select_wires('GW2A-18C')
        dev = SimpleNamespace(extra_func={}, nodes={})
        dat = self.make_dat(
            [-1, -1, -1, 6, 10],
            [-1, 46, 45, 43, 44, 39, 38, -1, 42, 40, 41],
        )

        chipdb.fse_create_jtag(dev, 'GW2A-18C', dat)

        jtag = dev.extra_func[(27, 50)]['jtag']
        self.assertEqual(jtag['inputs']['tdo_er1_i'], 'C1')
        self.assertEqual(jtag['inputs']['tdo_er2_i'], 'C2')
        self.assertEqual(jtag['outputs']['tck_o'], 'Q6')
        self.assertEqual(dev.nodes, {})


if __name__ == '__main__':
    unittest.main()
