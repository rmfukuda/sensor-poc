import asyncio
import sqlite3
import struct
from datetime import datetime
from typing import List, Tuple, Union

import plotly.graph_objects as go
from bleak import BleakClient, BleakScanner


class SqlData:
    """Class for handling SQLite database operations for sensor data.

    Attributes
    ----------
    con : sqlite3.Connection
        SQLite database connection.
    cursor : sqlite3.Cursor
        Cursor for executing SQL commands.
    """

    def __init__(self, filename: str = "sensor.db") -> None:
        """Class constructor.

        Parameters
        ----------
        filename
            The database filename.
        """
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

    def insert(self, reading_value: float = 25.5) -> None:
        """Insert sensor data into the database.

        Parameters
        ----------
        reading_value
            The sensor reading value to be inserted (default is 25.5).
        """
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

    def select(self) -> List[Tuple[int, float, str]]:
        """Select and retrieve sensor data from the database.

        Returns
        -------
        List[Tuple[int, float, str]]
            A list of tuples containing the retrieved sensor data.
            Each tuple contains (entry_id, sensor_value, timestamp).
        """
        # Read and print sensor data
        self.cursor.execute("SELECT * FROM SensorData")
        sensor_data = self.cursor.fetchall()

        print("Sensor Data:")
        for entry in sensor_data:
            print("EntryID:", entry[0])
            print("ReadingValue:", entry[1])
            print("Timestamp:", entry[2])
            print()
        return sensor_data


class BleData:
    """Class for handling BLE data from the ESP32 firmware.

    Attributes
    ----------
    notify_characteristic : str
        The UUID of the characteristic for notification.
    client : BleakClient
        The BLE client instance.
    sensor_data : List[float]
        A list to store the received sensor data.
    duration : Union[int, float]
        The duration in seconds for which BLE data will be received.
    sql : SqlData
        An instance of the SqlData class for database operations.
    """

    def __init__(self, duration: Union[int, float]) -> None:
        """Class constructor. Initialize the attributes of the BleData object.

        Parameters
        ----------
        duration
            The duration in seconds for which BLE data will be received.
        """
        self.notify_characteristic = "0000ff01-0000-1000-8000-00805f9b34fb"
        self.client = BleakClient("")
        self.sensor_data = []
        self.duration = duration
        self.sql = SqlData()

    async def main(self):
        """Start the BLE notification and receive sensor data.

        Raises
        ------
        Exception
            If an error occurs during the notification process.
        """
        try:
            firmware_device_name = "SENSOR_POC"
            device = await BleakScanner.find_device_by_name(firmware_device_name)
            self.client = BleakClient(device)
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

    def notify_callback(self, _, sensor_data: bytearray) -> None:
        """Callback function for handling incoming notifications.

        Parameters
        ----------
        _
            Unused.
        sensor_data
            The received sensor data.
        """
        float_value = struct.unpack("<f", sensor_data)[0]
        self.sensor_data.append(float_value)
        self.sql.insert(float_value)


def data_visualization(sql_query_result: List[Tuple[str, float, str]]) -> None:
    """Visualize temperature data over time.

    Parameters
    ----------
    sql_query_result
        A list of tuples representing temperature data queried from an SQL database.
        Each tuple contains three elements: (id, temperature, timestamp).

    Returns
    -------
    None
        The function does not return any value. It displays a plot of temperature
        data over time using Plotly.

    Notes
    -----
    This function takes the result of an SQL query containing temperature data
    and visualizes it over time using a line plot. The x-axis represents timestamps,
    and the y-axis represents temperatures in Celsius.

    Examples
    --------
    >>> data_visualization([(1, 23.5, '2022-01-01 12:00:00'), (2, 24.0, '2022-01-01 12:15:00')])
    """
    # Unpack the tuples into separate lists for timestamps and temperatures
    _, temperatures, timestamps = zip(*sql_query_result)

    # Convert timestamps to datetime objects
    timestamps = [datetime.strptime(ts, "%Y-%m-%d %H:%M:%S") for ts in timestamps]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=timestamps, y=temperatures, mode="lines+markers", name="Temperature"
        )
    )
    fig.update_layout(
        title="Temperature Over Time",
        xaxis_title="Timestamp",
        yaxis_title="Temperature (Celsius)",
        xaxis=dict(type="category"),
    )
    fig.update_yaxes(range=[0, 75])

    fig.show()


async def ble_receive(duration: Union[int, float]) -> None:
    """Routine to receive BLE data from the ESP32 firmware.

    Parameters
    ----------
    duration : Union[int, float]
        The duration in seconds for which BLE data will be received.
    """
    ble_obj = BleData(duration)
    await ble_obj.main()


if __name__ == "__main__":
    # example code:
    # sensor read
    duration = 5
    asyncio.run(ble_receive(duration))

    # read the database
    sql_obj = SqlData()
    sensor_data = sql_obj.select()

    # data plot
    data_visualization(sensor_data)
