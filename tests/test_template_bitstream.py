import unittest
from types import SimpleNamespace
from unittest.mock import Mock

import numpy as np

from apycula.gowin_pack import Bitstream, Bitstream_GW5A, CellFuseBits


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


if __name__ == '__main__':
    unittest.main()
