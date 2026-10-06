"""Tests for qconvert. Run with: python -m unittest"""

import unittest

from qconvert import convert_text, parse_value_unit, split_values


class ConversionTests(unittest.TestCase):
    def check(self, raw, expected):
        self.assertEqual(convert_text(raw), expected)

    def test_temperature(self):
        self.check("72f", "72F = 22.2C")
        self.check("22c", "22C = 71.6F")
        self.check("-40c", "-40C = -40F")

    def test_kelvin_is_not_supported(self):
        with self.assertRaises(ValueError):
            parse_value_unit("300k")

    def test_length(self):
        self.check("5ft", "5 ft = 1.52 m = 152.4 cm")
        self.check("180cm", "180 cm = 70.87 in = 5 ft 10.9 in")
        self.check("10km", "10 km = 6.21 mi")
        self.check("12in", "12 in = 30.48 cm")
        self.check("20cm", "20 cm = 7.87 in")  # under a foot: no ft/in breakdown

    def test_feet_and_inches_never_shows_12_inches(self):
        self.check("182.87cm", "182.87 cm = 72 in = 6 ft 0 in")

    def test_weight(self):
        self.check("150lb", "150 lb = 68.04 kg")
        self.check("12oz", "12 oz = 340.2 g")
        self.check("80kg", "80 kg = 176.4 lb")

    def test_volume(self):
        self.check("1 cup", "1 cup = 236.6 ml = 16 tbsp = 8 fl oz")
        self.check("2 cups", "2 cups = 473.2 ml = 32 tbsp = 16 fl oz")
        self.check("3 tbsp", "3 tbsp = 44.36 ml = 9 tsp")
        self.check("8 fl oz", "8 fl oz = 236.6 ml = 16 tbsp")
        self.check("15ml", "15 ml = 3.04 tsp = 1.01 tbsp")
        self.check("250ml", "250 ml = 8.45 fl oz = 1.06 cups")
        self.check("1 gal", "1 gal = 3.79 L = 4 qt")

    def test_speed(self):
        self.check("65mph", "65 mph = 104.6 kph")
        self.check("100 km/h", "100 kph = 62.14 mph")

    def test_data(self):
        self.check("4.7GB", "4.7 GB = 4.38 GiB")
        self.check("1TB", "1 TB = 931.3 GiB")
        self.check("1500MB", "1,500 MB = 1.5 GB = 1.4 GiB")
        self.check("16GiB", "16 GiB = 17.18 GB")

    def test_aliases_and_spacing(self):
        self.assertEqual(parse_value_unit("5 feet"), (5.0, "ft"))
        self.assertEqual(parse_value_unit("2 Fl. Oz."), (2.0, "floz"))
        self.assertEqual(parse_value_unit("150 LBS"), (150.0, "lb"))
        self.assertEqual(parse_value_unit("1,000 ft"), (1000.0, "ft"))

    def test_category_must_match_unit(self):
        with self.assertRaises(ValueError):
            convert_text("5ft", "weight")

    def test_missing_unit(self):
        with self.assertRaises(ValueError):
            parse_value_unit("72")


class SplitTests(unittest.TestCase):
    def test_split_values(self):
        self.assertEqual(split_values("72f 5 ft 2 fl oz -40c"), ["72f", "5 ft", "2 fl oz", "-40c"])


if __name__ == "__main__":
    unittest.main()
