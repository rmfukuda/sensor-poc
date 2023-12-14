import asyncio

from bleak import BleakClient


class BleData:
    def __init__(self, duration) -> None:
        address = "7C:DF:A1:E6:DF:DA"
        self.notify_characteristic = "0000ff01-0000-1000-8000-00805f9b34fb"
        self.client = BleakClient(address)
        self.sensor_data = []
        self.duration = duration

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
        self.sensor_data.append(sensor_data)


async def main(duration):
    ble_obj = BleData(duration)
    await ble_obj.main()
    print(ble_obj.sensor_data)


if __name__ == "__main__":
    duration = 10
    asyncio.run(main(duration))
