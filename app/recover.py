import subprocess
import time
import re
import argparse

UHUBCTL_PATH = "/sbin/uhubctl"

def run(args=None):
    unauthorized_serials = get_unauthorized_devices()
    if not unauthorized_serials:
        print("[INFO] unauthorized なデバイスは検出されませんでした。")
        return

    uhubctl_output = get_uhubctl_output()
    serial_port_map = extract_serial_to_hubport_map(uhubctl_output)

    print("\n[INFO] 検出された unauthorized デバイス:")
    for serial in unauthorized_serials:
        print(f"  - {serial}")

    print("\n[INFO] シリアルポートマップ:")
    for serial, ports in serial_port_map.items():
        for hub, port in ports:
            print(f"  {serial} → hub {hub} port {port}")

    for serial in unauthorized_serials:
        if serial in serial_port_map:
            for hub, port in serial_port_map[serial]:
                toggle_port(hub, port)
        else:
            print(f"[WARN] 該当ポートが見つかりません: {serial}")

def get_unauthorized_devices():
    result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
    lines = result.stdout.strip().splitlines()[1:]
    return [line.split()[0] for line in lines if "\tunauthorized" in line]

def get_uhubctl_output():
    print("[INFO] sudo を使用して uhubctl を実行します。パスワードを求められる場合があります。")
    result = subprocess.run(["sudo", UHUBCTL_PATH], capture_output=True, text=True)
    return result.stdout

def extract_serial_to_hubport_map(uhubctl_output):
    serial_map = {}
    current_hub = None

    for line in uhubctl_output.splitlines():
        hub_match = re.match(r"Current status for hub ([\w\-\.]+)", line)
        if hub_match:
            current_hub = hub_match.group(1)
            continue

        if current_hub and "connect" in line and "[" in line:
            port_match = re.search(r"Port (\d+): .*connect.*\[(.+?)\]$", line)
            if port_match:
                port = int(port_match.group(1))
                content = port_match.group(2).strip()
                parts = content.split()
                if parts:
                    serial = parts[-1].strip()
                    if serial not in serial_map:
                        serial_map[serial] = []
                    serial_map[serial].append((current_hub, port))
    return serial_map

def toggle_port(hub, port):
    print(f"[INFO] 再起動: hub {hub}, port {port}")
    subprocess.run(["sudo", UHUBCTL_PATH, "-l", hub, "-p", str(port), "-a", "0"])
    time.sleep(2)
    subprocess.run(["sudo", UHUBCTL_PATH, "-l", hub, "-p", str(port), "-a", "1"])
    time.sleep(5)

def main():
    parser = argparse.ArgumentParser(
        prog='droid-recover',
        description='Auto-recover unauthorized Android devices by toggling USB ports.\n'
                    'This command detects devices in "unauthorized" state and attempts\n'
                    'to recover them by power-cycling their USB ports using uhubctl.\n'
                    '\n'
                    'This is useful when devices lose authorization due to connection issues.',
        epilog='Examples:\n'
               '  droid-recover           # Recover all unauthorized devices\n'
               '\n'
               'Process:\n'
               '  1. Detect unauthorized devices via "adb devices"\n'
               '  2. Map devices to USB hub ports using uhubctl\n'
               '  3. Power off USB port (2 seconds)\n'
               '  4. Power on USB port (5 seconds wait)\n'
               '  5. Device should prompt for authorization again\n'
               '\n'
               'Requirements:\n'
               '  - uhubctl must be installed at /sbin/uhubctl\n'
               '  - sudo access required (may prompt for password)\n'
               '  - USB hubs must support per-port power switching\n'
               '\n'
               'Troubleshooting:\n'
               '  - If devices not found: check USB hub compatibility\n'
               '  - After recovery: manually approve authorization on device\n'
               '  - Some USB hubs do not support power switching\n'
               '\n'
               'Note: This command takes no additional arguments.',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    run()

