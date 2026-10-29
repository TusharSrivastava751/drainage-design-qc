import unittest
from drainage_qc import screen

CONFIG = {'minimum_cover_m': 0.9, 'full_flow_velocity_min_m_s': 0.6, 'full_flow_velocity_max_m_s': 3.0}
BASE = dict(pipe_id='TEST', length_m=100, diameter_mm=1000, outside_diameter_mm=1100, invert_up_m=10,
            invert_down_m=9, ground_up_m=13, ground_down_m=12, manning_n=0.01,
            catchment_ha=1, runoff_coefficient=1, intensity_mm_hr=360)

class DrainageTests(unittest.TestCase):
    def test_hand_calculation(self):
        r = screen([BASE], CONFIG)['results'][0]
        self.assertAlmostEqual(r['demand_m3_s'], 1)
        self.assertAlmostEqual(r['full_flow_capacity_m3_s'], 3.116854677, places=7)
        self.assertAlmostEqual(r['minimum_endpoint_cover_m'], 1.9)

    def test_adverse_slope_does_not_get_capacity(self):
        r = screen([dict(BASE, invert_down_m=11)], CONFIG)['results'][0]
        self.assertIsNone(r['full_flow_capacity_m3_s'])
        self.assertIn('NON_POSITIVE_SLOPE', r['findings'])

    def test_overload_and_cover(self):
        r = screen([dict(BASE, diameter_mm=100, ground_up_m=10)], CONFIG)['results'][0]
        self.assertIn('DEMAND_EXCEEDS_FULL_FLOW_REFERENCE', r['findings'])
        self.assertIn('COVER_BELOW_DEMO_LIMIT', r['findings'])

    def test_zero_runoff(self):
        r = screen([dict(BASE, runoff_coefficient=0)], CONFIG)['results'][0]
        self.assertEqual(r['demand_capacity_ratio'], 0)

    def test_invalid_physical_values(self):
        for key, value in [('length_m',0), ('diameter_mm',-1), ('manning_n',0), ('catchment_ha',-1), ('runoff_coefficient',1.01), ('intensity_mm_hr','NaN')]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                screen([dict(BASE, **{key:value})], CONFIG)

    def test_duplicate_pipe(self):
        with self.assertRaises(ValueError):
            screen([BASE, BASE], CONFIG)

    def test_bad_criteria(self):
        with self.assertRaises(ValueError):
            screen([BASE], dict(CONFIG, full_flow_velocity_min_m_s=4))

    def test_outside_diameter_must_cover_internal_diameter(self):
        with self.assertRaises(ValueError):
            screen([dict(BASE, outside_diameter_mm=900)], CONFIG)
