"""Scan for nearby BLE devices. Run with scooter powered on."""
import asyncio

from bleak import BleakScanner


async def main() -> None:
    print("Scanning 10s ...")
    found = await BleakScanner.discover(timeout=10, return_adv=True)
    for _, (dev, adv) in sorted(
        found.items(), key=lambda kv: kv[1][1].rssi or -999, reverse=True
    ):
        name = dev.name or adv.local_name or "(no name)"
        marker = " <=== NIU" if "NIU" in name.upper() else ""
        print(f"{name:35} {dev.address}  rssi={adv.rssi}{marker}")


if __name__ == "__main__":
    asyncio.run(main())
