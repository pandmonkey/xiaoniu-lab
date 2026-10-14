#!/usr/bin/env python3
"""NIU Link 解速/恢复限速 — 极简版。

用法:
  pip install bleak
  python niu_link_minimal.py "NIU Link 1691"          # 解速
  python niu_link_minimal.py "NIU Link 1691" --lock   # 恢复限速

前置: 手机小牛 App 先连一次车, 然后彻底退出 App, 再跑本脚本。
"""
import asyncio
import sys

from bleak import BleakClient, BleakScanner

UNLOCK = bytes.fromhex("6784855911124499612592282354227987263531")
LOCK   = bytes.fromhex("6784568726353113346130602277419687263531")


async def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit("usage: niu_link_minimal.py <设备名> [--lock]")
    name = args[0]
    payload = LOCK if "--lock" in sys.argv else UNLOCK

    dev = await BleakScanner.find_device_by_filter(
        lambda d, a: (d.name or a.local_name or "") == name, timeout=15
    )
    if not dev:
        sys.exit(f"找不到 {name}, 确认车开机且手机 App 已退出")

    async with BleakClient(dev) as c:
        for svc in c.services:
            for ch in svc.characteristics:
                w = "write" in ch.properties or "write-without-response" in ch.properties
                if not w or ch.uuid.startswith("0000"):
                    continue
                await c.write_gatt_char(
                    ch, payload,
                    response="write-without-response" not in ch.properties,
                )
                print(f"已发送 -> {ch.uuid}")
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
