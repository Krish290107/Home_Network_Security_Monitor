OUI_DATABASE = {
    "A4:83:E7": "Apple",
    "AC:DE:48": "Apple",
    "F0:18:98": "Apple",
    "3C:22:FB": "Apple",
    "DC:A9:04": "Apple",
    "78:7B:8A": "Apple",
    "88:66:A5": "Apple",
    "A8:5C:2C": "Apple",
    "F4:5C:89": "Apple",
    "14:7D:DA": "Apple",
    "98:01:A7": "Apple",
    "BC:D0:74": "Apple",
    "28:6A:BA": "Apple",

    "A0:59:50": "Samsung",
    "8C:F5:A3": "Samsung",
    "00:26:37": "Samsung",
    "F8:04:2E": "Samsung",
    "54:40:AD": "Samsung",
    "E4:7D:BD": "Samsung",
    "B0:72:BF": "Samsung",
    "CC:07:AB": "Samsung",
    "64:B5:C6": "Samsung",
    "34:23:BA": "Samsung",
    "A8:7C:01": "Samsung",

    "00:14:22": "Dell",
    "18:A9:9B": "Dell",
    "F8:BC:12": "Dell",
    "B0:83:FE": "Dell",
    "D4:BE:D9": "Dell",
    "00:1A:A0": "Dell",
    "00:1E:4F": "Dell",
    "14:18:77": "Dell",
    "24:6E:96": "Dell",
    "34:17:EB": "Dell",

    "00:1A:4B": "HP",
    "3C:D9:2B": "HP",
    "94:57:A5": "HP",
    "FC:15:B4": "HP",
    "00:21:5A": "HP",
    "2C:27:D7": "HP",
    "D4:C9:EF": "HP",
    "10:60:4B": "HP",

    "28:D2:44": "Lenovo",
    "54:EE:75": "Lenovo",
    "E8:2A:44": "Lenovo",
    "5C:80:B6": "Lenovo",
    "98:FA:9B": "Lenovo",
    "00:09:2D": "Lenovo",

    "00:1B:21": "Intel",
    "3C:97:0E": "Intel",
    "68:05:CA": "Intel",
    "A4:C4:94": "Intel",
    "8C:8D:28": "Intel",
    "34:13:E8": "Intel",
    "AC:74:B1": "Intel",

    "28:6C:07": "Xiaomi",
    "FC:64:BA": "Xiaomi",
    "78:11:DC": "Xiaomi",
    "9C:99:A0": "Xiaomi",
    "64:B4:73": "Xiaomi",
    "58:44:98": "Xiaomi",
    "8C:DE:F9": "Xiaomi",

    "50:C7:BF": "TP-Link",
    "14:EB:B6": "TP-Link",
    "EC:08:6B": "TP-Link",
    "C0:06:C3": "TP-Link",
    "70:4F:57": "TP-Link",
    "30:B5:C2": "TP-Link",
    "B0:BE:76": "TP-Link",

    "A4:2B:8C": "Netgear",
    "C4:04:15": "Netgear",
    "28:C6:8E": "Netgear",
    "6C:B0:CE": "Netgear",
    "84:1B:5E": "Netgear",
    "E0:46:9A": "Netgear",

    "00:1A:92": "ASUS",
    "2C:4D:54": "ASUS",
    "AC:9E:17": "ASUS",
    "30:85:A9": "ASUS",
    "04:D4:C4": "ASUS",
    "1C:87:2C": "ASUS",

    "F4:F5:D8": "Google",
    "54:60:09": "Google",
    "A4:77:33": "Google",
    "30:FD:38": "Google",
    "F8:8F:CA": "Google",

    "FC:65:DE": "Amazon",
    "A0:02:DC": "Amazon",
    "44:65:0D": "Amazon",
    "74:C2:46": "Amazon",
    "68:54:FD": "Amazon",
    "84:D6:D0": "Amazon",

    "00:15:5D": "Microsoft",
    "00:50:F2": "Microsoft",
    "28:18:78": "Microsoft",
    "7C:1E:52": "Microsoft",
    "DC:B4:C4": "Microsoft",

    "B8:27:EB": "Raspberry Pi",
    "DC:A6:32": "Raspberry Pi",
    "E4:5F:01": "Raspberry Pi",
    "28:CD:C1": "Raspberry Pi",
    "D8:3A:DD": "Raspberry Pi",

    "00:1A:2B": "Cisco",
    "00:1B:0D": "Cisco",
    "00:1E:F7": "Cisco",
    "58:AC:78": "Cisco",
    "68:BD:AB": "Cisco",
    "B0:AA:77": "Cisco",

    "00:1C:F0": "D-Link",
    "14:D6:4D": "D-Link",
    "28:10:7B": "D-Link",
    "1C:7E:E5": "D-Link",
    "C8:D3:A3": "D-Link",

    "00:E0:FC": "Huawei",
    "48:46:FB": "Huawei",
    "70:72:3C": "Huawei",
    "A4:BE:2B": "Huawei",
    "CC:A2:23": "Huawei",
    "88:66:39": "Huawei",

    "00:04:1F": "Sony",
    "00:13:A9": "Sony",
    "00:1D:BA": "Sony",
    "28:0D:FC": "Sony",
    "AC:89:95": "Sony",

    "00:1C:62": "LG",
    "10:68:3F": "LG",
    "A8:23:FE": "LG",
    "CC:FA:00": "LG",
    "64:99:5D": "LG",

    "94:65:2D": "OnePlus",
    "C0:EE:40": "OnePlus",

    "00:E0:4C": "Realtek",
    "52:54:00": "Realtek",

    "00:0C:29": "VMware",
    "00:50:56": "VMware",
    "00:05:69": "VMware",

    "C0:25:E9": "TP-Link",
    "20:6B:E7": "TP-Link",
    "60:32:B1": "TP-Link",
}

def lookup_vendor(mac_address):

    if not mac_address:
        return "Unknown"

    mac = mac_address.upper().replace("-", ":")

    parts = mac.split(":")

    if len(parts) < 3:
        return "Unknown"

    oui = ":".join(parts[:3])

    return OUI_DATABASE.get(oui, "Unknown")

def enrich_devices(devices):

    for device in devices:

        mac = device.get("mac", "")

        device["vendor"] = lookup_vendor(mac)

    return devices
