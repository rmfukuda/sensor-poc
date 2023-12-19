import sqlite3
import unittest

from main import SqlData


class TestSqlData(unittest.TestCase):
    def setUp(self):
        self.filename = "test_sensor.db"
        self.sql_data = SqlData(filename=self.filename)

    def tearDown(self):
        # Clean up the test database after each test
        with sqlite3.connect(self.filename) as conn:
            conn.execute("DROP TABLE IF EXISTS SensorData")

    def test_insert_and_select(self):
        # Test the insert and select methods
        reading_value = 30.0
        self.sql_data.insert(reading_value=reading_value)

        sensor_data = self.sql_data.select()
        self.assertEqual(len(sensor_data), 1)
        self.assertEqual(sensor_data[0][1], reading_value)

    def test_insert_default_value(self):
        # Test the insert method with default reading value
        self.sql_data.insert()

        sensor_data = self.sql_data.select()
        self.assertEqual(len(sensor_data), 1)
        self.assertEqual(sensor_data[0][1], 25.5)


if __name__ == "__main__":
    unittest.main()
