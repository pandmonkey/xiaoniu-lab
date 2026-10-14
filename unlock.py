"""Send the speed-limit unlock/relock frame to a NIU Link scooter.

Payloads come from the community-documented nRF Connect method:
connect once with the official NIU app first, kill it, then write the
20-byte hex frame to the writable "Unknown Characteristic".

Usage:
  python unlock.py "NIU Link 1691"            # send unlock
  python unlock.py "NIU Link 1691" --lock     # send relock (restore limit)
  python unlock.py "NIU Link 1691" --uuid <char-uuid>
"""
import asyncio
import sys

from bleak import BleakClient, BleakScanner
from bleak.exc import BleakError

UNLOCK_HEX = "6784855911124499612592282354227987263531"
RELOCK_HEX = "6784568726353113346130602277419687263531"


def is_standard_uuid(uuid: str) -> bool:
    # 16-bit assigned-number UUIDs look like 00002a00-0000-1000-8000-00805f9b34fb
    return uuid.startswith("0000") and uuid.endswith("-0000-1000-8000-00805f9b34fb")


async def main() -> None:
    argv = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not argv:
        sys.exit("usage: unlock.py <device-name> [--lock] [--uuid <char>]")
    target = argv[0]

    payload = bytes.fromhex(RELOCK_HEX if "--lock" in sys.argv else UNLOCK_HEX)
    only_uuid = None
    if "--uuid" in sys.argv:
        only_uuid = sys.argv[sys.argv.index("--uuid") + 1].lower()

    print(f"Scanning for {target!r} ...")
    dev = await BleakScanner.find_device_by_filter(
        lambda d, adv: (d.name or adv.local_name or "").upper() == target.upper(),
        timeout=15,
    )
    if not dev:
        print(f"{target!r} not found")
        return


    print(f"Connecting {dev.name} {dev.address}")
    async with BleakClient(dev) as client:
        # subscribe to all notifiable characteristics so we can see replies
        def on_notify(c, data: bytearray) -> None:
            print(f"<<< notify {c.uuid}: {bytes(data).hex()}")

        for svc in client.services:
            for c in svc.characteristics:
                if "notify" in c.properties:
                    try:
                        await client.start_notify(c, on_notify)
                        print(f"subscribed {c.uuid}")
                    except BleakError as e:
                        print(f"subscribe {c.uuid} failed: {e}")
        candidates = []
        for svc in client.services:
            for c in svc.characteristics:
                writable = "write" in c.properties or "write-without-response" in c.properties
                if not writable:
                    continue
                print(f"writable char {c.uuid}  [{','.join(c.properties)}]")
                if only_uuid or not is_standard_uuid(c.uuid):
                    candidates.append(c)

        if only_uuid:
            candidates = [c for c in candidates if c.uuid.lower() == only_uuid]
        if not candidates:
            print("no writable vendor characteristic found; run explore.py")
            return

        for c in candidates:
            use_rsp = "write-without-response" not in c.properties
            try:
                await client.write_gatt_char(c, payload, response=use_rsp)
                print(f"sent {payload.hex()} -> {c.uuid}")
            except BleakError as e:
                print(f"write to {c.uuid} failed: {e}")

        await asyncio.sleep(3)  # collect any late notifications


if __name__ == "__main__":
    asyncio.run(main())
