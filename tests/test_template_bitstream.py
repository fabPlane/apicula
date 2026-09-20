import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import numpy as np

from apycula.gowin_pack import (
    Bitstream,
    Bitstream_GW5A,
    CellFuseBits,
    GW5A,
    GW5AST_138C,
)


class TemplateBitstreamTests(unittest.TestCase):
    def test_fuses_are_merged_before_replacing_template_domain(self):
        output = Bitstream.__new__(Bitstream)
        output.main_tilemap = np.empty((1, 1), dtype=object)
        output.main_tilemap[0, 0] = np.zeros((1, 3), dtype=np.uint8)

        chipdb = SimpleNamespace(
            db=SimpleNamespace(template=[[0]]),
            get_fuse_domain=Mock(return_value={(0, 0), (0, 1), (0, 2)}),
        )
        output.device = SimpleNamespace(chipdb=chipdb)

        output.set_fuses([
            CellFuseBits(0, 0, {(0, 0)}),
            CellFuseBits(0, 0, {(0, 1)}),
        ])

        chipdb.get_fuse_domain.assert_called_once_with(
            0, 0, {(0, 0), (0, 1)})
        np.testing.assert_array_equal(
            output.main_tilemap[0, 0], np.array([[1, 1, 0]]))

    def test_extra_rows_are_written_but_excluded_from_checksum(self):
        output = Bitstream_GW5A.__new__(Bitstream_GW5A)
        tile_grid = np.array([[0, 1, 0], [1, 0, 1]], dtype=np.uint8)
        extra_rows = [[1, 1, 0]]
        output.main_tilemap = object()
        output.device = SimpleNamespace(
            chipdb=SimpleNamespace(
                db=SimpleNamespace(template_extra=extra_rows)),
            fuse_bitmap=Mock(return_value=tile_grid),
            has_bsram_init_data=Mock(return_value=False),
        )
        output.fill_header_footer = Mock()
        output.write_without_bsram = Mock()

        output.write()

        checksum_map = output.fill_header_footer.call_args.args[0]
        emitted_map = output.write_without_bsram.call_args.args[0]
        np.testing.assert_array_equal(checksum_map, tile_grid.T)
        np.testing.assert_array_equal(
            emitted_map, np.vstack((tile_grid, extra_rows)).T)

    def test_older_database_without_extra_rows_is_supported(self):
        output = Bitstream_GW5A.__new__(Bitstream_GW5A)
        tile_grid = np.array([[0, 1], [1, 0]], dtype=np.uint8)
        output.main_tilemap = object()
        output.device = SimpleNamespace(
            chipdb=SimpleNamespace(db=SimpleNamespace()),
            fuse_bitmap=Mock(return_value=tile_grid),
            has_bsram_init_data=Mock(return_value=False),
        )
        output.fill_header_footer = Mock()
        output.write_without_bsram = Mock()

        output.write()

        emitted_map = output.write_without_bsram.call_args.args[0]
        np.testing.assert_array_equal(emitted_map, tile_grid.T)


class GW5ASTDualPinTests(unittest.TestCase):
    @staticmethod
    def make_device(ready, done):
        device = GW5AST_138C.__new__(GW5AST_138C)
        device.cli_args = SimpleNamespace(args=SimpleNamespace(
            ready_as_gpio=ready,
            done_as_gpio=done,
        ))
        return device

    def test_ready_and_done_gpio_add_combined_encoding(self):
        device = self.make_device(True, True)
        tilemap = {
            (108, 170): np.zeros((6, 72), dtype=np.uint8),
        }

        with patch.object(GW5A, 'fuse_bitmap', return_value='bitmap'):
            result = device.fuse_bitmap(tilemap)

        self.assertEqual(result, 'bitmap')
        self.assertEqual(tilemap[108, 170][4][28], 1)
        self.assertEqual(tilemap[108, 170][5][23], 1)
        self.assertEqual(tilemap[108, 170][2][68], 1)
        self.assertEqual(tilemap[108, 170][2][71], 1)

    def test_combined_encoding_requires_both_options(self):
        for ready, done in ((False, False), (True, False), (False, True)):
            with self.subTest(ready=ready, done=done):
                device = self.make_device(ready, done)
                tilemap = {
                    (108, 170): np.zeros((6, 72), dtype=np.uint8),
                }
                with patch.object(GW5A, 'fuse_bitmap', return_value='bitmap'):
                    device.fuse_bitmap(tilemap)
                self.assertEqual(tilemap[108, 170][2][68], 0)
                self.assertEqual(tilemap[108, 170][2][71], 0)
                route_value = 1 if ready else 0
                self.assertEqual(tilemap[108, 170][4][28], route_value)
                self.assertEqual(tilemap[108, 170][5][23], route_value)


if __name__ == '__main__':
    unittest.main()
