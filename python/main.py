import asyncio
import sqlite3
import struct
from datetime import datetime

from bleak import BleakClient


class SqlData:
    def __init__(self) -> None:
        filename = "sensor.db"
        self.con = sqlite3.connect(filename)
        self.cursor = self.con.cursor()
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS SensorData (
                entry_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                sensor REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
            )
        """
        )

    def insert(self, reading_value=25.5):
        # Insert sample sensor data
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.cursor.execute(
            """
            INSERT INTO SensorData (sensor, timestamp)
            VALUES (?, ?)
        """,
            (reading_value, timestamp),
        )
        self.con.commit()

    def select(self):
        # Read and print sensor data
        self.cursor.execute("SELECT * FROM SensorData")
        sensor_data = self.cursor.fetchall()

        print("Sensor Data:")
        for entry in sensor_data:
            print("EntryID:", entry[0])
            print("ReadingValue:", entry[1])
            print("Timestamp:", entry[2])
            print()


class BleData:
    def __init__(self, duration) -> None:
        address = "7C:DF:A1:E6:DF:DA"
        self.notify_characteristic = "0000ff01-0000-1000-8000-00805f9b34fb"
        self.client = BleakClient(address)
        self.sensor_data = []
        self.duration = duration
        self.sql = SqlData()

    async def main(self):
        try:
            await self.client.connect()
            print(self.client.is_connected)
            await self.client.start_notify(
                self.notify_characteristic, self.notify_callback
            )
            await asyncio.sleep(self.duration)
        except Exception as excp:
            print(excp)
        finally:
            await self.client.stop_notify(self.notify_characteristic)
            await self.client.disconnect()

    def notify_callback(self, characteristic_handle, sensor_data):
        # convert bytearray into float
        float_value = struct.unpack("<f", sensor_data)[0]
        self.sensor_data.append(float_value)
        self.sql.insert(float_value)


async def main(duration):
    ble_obj = BleData(duration)
    await ble_obj.main()
    print(ble_obj.sensor_data)


if __name__ == "__main__":
    duration = 5
    asyncio.run(main(duration))

    # database read
    sql_obj = SqlData()
    sql_obj.select()
