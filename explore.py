"""Connect to a NIU device and dump its GATT table.

Usage: python explore.py [name-prefix]   (default "NIU")
"""
import asyncio
import sys

from bleak import BleakClient, BleakScanner


async def main() -> None:
    prefix = sys.argv[1] if len(sys.argv) > 1 else "NIU"
    dev = await BleakScanner.find_device_by_filter(
        lambda d, adv: (d.name or adv.local_name or "").upper()
        .startswith(prefix.upper()),
        timeout=15,
    )
    if not dev:
        print("not found")
        return
    print(f"Connecting {dev.name} {dev.address}")
    async with BleakClient(dev) as client:
        for svc in client.services:
            print(f"\nservice {svc.uuid}")
            for c in svc.characteristics:
                print(f"  char {c.uuid}  [{','.join(c.properties)}]")
                for d in c.descriptors:
                    print(f"    desc {d.uuid}")


if __name__ == "__main__":
    asyncio.run(main())
