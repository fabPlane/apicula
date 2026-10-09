import unittest
from types import SimpleNamespace

from apycula import gowin_pack


class GW5ASTElvdsTests(unittest.TestCase):
    @staticmethod
    def device(device_name, true_lvds=True):
        device = object.__new__(gowin_pack.Device)
        device.device_name = device_name
        device.chipdb = SimpleNamespace(
            get_io_diff_cfg=lambda _x, _y, _idx: SimpleNamespace(
                true_lvds=true_lvds, positive=True))
        return device

    @staticmethod
    def bel(cell_type):
        return SimpleNamespace(
            x=181, y=104, idx_str='A',
            cell=SimpleNamespace(name='hdmi', typ=cell_type,
                                 parms={'DIFF': 'P'}))

    def test_gw5ast_allows_emulated_output_on_true_lvds_pair(self):
        device = self.device('GW5AST-138C')
        device.check_elvds_placement(self.bel('ELVDS_OBUF'))
        device.check_elvds_placement(self.bel('ELVDS_TBUF'))

    def test_gw5ast_still_rejects_emulated_input_on_true_lvds_pair(self):
        with self.assertRaisesRegex(Exception, 'True LVDS pin'):
            self.device('GW5AST-138C').check_elvds_placement(
                self.bel('ELVDS_IBUF'))

    def test_other_devices_still_reject_true_lvds_pair(self):
        with self.assertRaisesRegex(Exception, 'True LVDS pin'):
            self.device('GW5A-25A').check_elvds_placement(
                self.bel('ELVDS_OBUF'))


if __name__ == '__main__':
    unittest.main()
