import psutil
import platform
import time


def system_monitor() -> str:
    try:
        cpu_pct = psutil.cpu_percent(interval=0.1)
        cpu_count = psutil.cpu_count(logical=True)
        
        vm = psutil.virtual_memory()
        ram_used_gb = vm.used / (1024 ** 3)
        ram_total_gb = vm.total / (1024 ** 3)
        ram_pct = vm.percent

        disk = psutil.disk_usage('C:\\')
        disk_used_gb = disk.used / (1024 ** 3)
        disk_total_gb = disk.total / (1024 ** 3)
        disk_pct = disk.percent

        battery_info = ""
        battery = psutil.sensors_battery()
        if battery:
            plugged = "Zaryadlanmoqda" if battery.power_plugged else "Batareyada"
            battery_info = f"Batareya: {battery.percent}% ({plugged})\n"

        boot_time = psutil.boot_time()
        uptime_h = int((time.time() - boot_time) // 3600)
        uptime_m = int(((time.time() - boot_time) % 3600) // 60)

        net1 = psutil.net_io_counters()
        time.sleep(0.3)
        net2 = psutil.net_io_counters()
        rx_kbs = ((net2.bytes_recv - net1.bytes_recv) / 0.3) / 1024
        tx_kbs = ((net2.bytes_sent - net1.bytes_sent) / 0.3) / 1024
        
        rx_str = f"{rx_kbs / 1024:.1f} MB/s" if rx_kbs > 1024 else f"{rx_kbs:.0f} KB/s"
        tx_str = f"{tx_kbs / 1024:.1f} MB/s" if tx_kbs > 1024 else f"{tx_kbs:.0f} KB/s"

        report = (
            f"[TIZIM HOLATI]\n"
            f"- CPU: {cpu_pct}% ({cpu_count} ta yadro)\n"
            f"- RAM: {ram_used_gb:.1f} GB / {ram_total_gb:.1f} GB ({ram_pct}%)\n"
            f"- Disk (C:): {disk_used_gb:.1f} GB / {disk_total_gb:.1f} GB ({disk_pct}%)\n"
            f"- Internet Tezligi: Yuklash (Download): {rx_str} | Yuborish (Upload): {tx_str}\n"
            f"{battery_info}"
            f"- Ish vaqti: {uptime_h} soat {uptime_m} daqiqa\n"
            f"- Tizim: {platform.system()} {platform.release()}"
        )
        return report

    except Exception as e:
        return f"Tizim monitoringida xatolik: {e}"
