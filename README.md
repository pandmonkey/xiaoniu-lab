# xiaoniu-lab

NIU Link 中控 BLE 解速工具。已在 `NIU Link 1691` 上实测生效。

## 原理

国内版 NIU Link 中控暴露一个私有 BLE 服务，向可写特征值写入
20 字节 hex 帧即可切换限速状态，无需鉴权（官方 App 先连一次
完成唤醒/放行，之后任意 BLE 中心都能写）。

- 解速帧: `6784855911124499612592282354227987263531`
- 恢复帧: `6784568726353113346130602277419687263531`

## 用法

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

1. 手机小牛 App 连一次车 → 彻底杀后台（BLE 只允许一个中心）
2. `open niu.command`（macOS：借 Terminal 拿蓝牙权限）
3. 菜单里 scan → explore → unlock；`4` 恢复限速

朋友版：`niu_link_minimal.py` 单文件，`pip install bleak` 即可，
设备名换成自己的。

## 文件

| 文件 | 作用 |
|---|---|
| `scan.py` | 扫附近 BLE 设备 |
| `explore.py` | 连车 dump GATT 表 |
| `unlock.py` | 发包解速/恢复（订阅 notify 打印回包） |
| `niu_link_minimal.py` | 极简可分享版 |
| `niu.command` | macOS Terminal 入口菜单 |

## GATT（NIU Link 1691 实测）

```
service 61751276-fdd6-11ed-be56-0242ac120002   # 私有调试口
  char 99ea30e2  [write-without-response]       # ← 大概率收包口
  char 7ee484ea  [read,notify]
service 8ec94e30-f315-4f60-9fb8-838830daea52   # NIU 主服务(同 KQi 家族)
  char 8ec94e31  [read,notify]
  char 8ec94e32  [read,write,write-without-response]
  char 8ec94e33  [read,write,write-without-response]
```

发包无回执，验证靠实际骑行。

## 注意

- 解速后不符合新国标 25km/h，事故/保险/责任自行承担
- 恢复限速 = 发第二串码，或换 `--lock` / 菜单 `4`
- 海外 KQi 系列是另一套（AES 鉴权 + 云端取密码），见
  github.com/bryanjonas/ScooterHacking
