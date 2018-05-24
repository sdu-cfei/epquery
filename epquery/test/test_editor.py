import unittest
import os
import shutil
import tempfile
import epquery as epq
import epquery.download as download


class TestEditor(unittest.TestCase):

    def setUp(self):
        # Temporary directory
        self.tempdir = tempfile.mkdtemp()
        print("Temp dir created: {}".format(self.tempdir))

        # Download IDF
        self.idf = os.path.join(self.tempdir, '1ZoneUncontrolled.idf')
        download.get_test_idf(name='1ZoneUncontrolled', ver='8.8.0', 
            save_path=self.idf)
        assert os.path.exists(self.idf)
        print("IDF downloaded: {}".format(self.idf))

        # Download IDD
        self.idd = os.path.join(self.tempdir, 'Energy+.idd')
        download.get_idd(8, self.idd)
        assert os.path.exists(self.idd)
        print("IDD downloaded: {}".format(self.idd))

    def tearDown(self):
        shutil.rmtree(self.tempdir)
        assert not os.path.exists(self.tempdir)
        print("Temp dir removed: {}".format(self.tempdir))

    def test_logger(self):
        # Delete already existing log file (if any)
        cwd = os.getcwd()
        log_file = os.path.join(cwd, 'epquery.log')
        if os.path.exists(log_file):
            os.remove(log_file)
        self.assertFalse(os.path.exists(log_file))

        # Check if log file correctly created
        editor = epq.Editor(self.idf, self.idd, config_logger=True)
        self.assertTrue(os.path.exists(log_file))

    def test_simple_queries(self):
        editor = epq.Editor(self.idf, self.idd)

        # mask + get_field
        zone_mask = editor.mask('Zone')
        zone_name = editor.get_field(zone_mask, 'Name')
        self.assertEqual(zone_name, 'ZONE ONE')

        # query + get_field
        bdg = editor.query('Building')
        bdg_name = editor.get_field(bdg, 'Terrain')
        self.assertEqual(bdg_name, 'Suburbs')

        # mask + filter + multiple objects + substring search
        mat_mask = editor.mask('Material:NoMass', method='substring', Name='LAYER')
        mat_obj_list = editor.filter(mat_mask)
        self.assertEqual(len(mat_obj_list), 2)

        # mask + inexact attribute names
        mat_mask = editor.mask('Material:NoMass', Thermal_Resistance_m2_K_W='5.456')
        mat_name = editor.get_field(mat_mask, 'Name')
        self.assertEqual(mat_name, 'R31LAYER')

    def test_set_field(self):
        editor = epq.Editor(self.idf, self.idd)
        m = editor.mask('RunPeriod')
        # Single-word field name
        editor.set_field(m, Name='Test')
        name = editor.get_field(m, 'Name')
        self.assertEqual(name, 'Test')
        # Multi-word field name
        editor.set_field(m, Day_of_Week_for_Start_Day='Test')
        day = editor.get_field(m, 'Day of Week for Start Day')
        self.assertEqual(day, 'Test')

if __name__ == "__main__":
    unittest.main(verbosity=2)
