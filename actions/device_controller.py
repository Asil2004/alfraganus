import os
import sys
import time
import socket
import subprocess
import json
import re
from pathlib import Path


def get_local_ip() -> str:
    """Kompyuterning mahalliy IP manzilini aniqlaydi"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def scan_network_devices() -> str:
    """Mahalliy Wi-Fi/LAN tarmoqdagi ulangan barcha qurilmalarni (Telefonlar, Smart TV, Router, IoT) skanerlaydi"""
    try:
        res = subprocess.run(["arp", "-a"], capture_output=True, text=True)
        lines = res.stdout.splitlines()
        devices = []
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 2 and re.match(r"^\d+\.\d+\.\d+\.\d+$", parts[0]):
                ip, mac = parts[0], parts[1]
                if not ip.endswith(".255") and ip != "255.255.255.255" and not ip.startswith("224.") and not ip.startswith("239."):
                    devices.append(f"• IP: {ip} | MAC: {mac}")
        
        local_ip = get_local_ip()
        if devices:
            dev_list = "\n".join(devices[:20])
            return f"Mahalliy tarmoqdagi (Wi-Fi: {local_ip}) faol qurilmalar:\n{dev_list}\nJami {len(devices)} ta qurilma aniqlandi."
        return "Tarmoqda faol tashqi qurilmalar topilmadi."
    except Exception as e:
        return f"Tarmoqni skanerlashda xatolik: {e}"


def list_bluetooth_devices() -> str:
    """Kompyuterga ulangan yoki juftlangan Bluetooth qurilmalarni (Telefon, Quloqchin, Smartwatch) aniqlaydi"""
    try:
        ps_cmd = "Get-PnpDevice -Class Bluetooth | Where-Object {$_.Status -eq 'OK'} | Select-Object -ExpandProperty FriendlyName"
        res = subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, text=True)
        names = [n.strip() for n in res.stdout.splitlines() if n.strip()]
        if names:
            return "Faol Bluetooth qurilmalari:\n" + "\n".join([f"• {n}" for n in names[:15]])
        return "Ulangan Bluetooth qurilmalari topilmadi."
    except Exception as e:
        return f"Bluetooth qurilmalarini tekshirishda xatolik: {e}"


def list_serial_com_ports() -> str:
    """Kompyuterga ulangan mikrokontrollerlar (Arduino, ESP32, CNC, Tokarlik, Lazer) COM portlarini aniqlaydi"""
    try:
        ps_cmd = "[System.IO.Ports.SerialPort]::GetPortNames()"
        res = subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, text=True)
        ports = [p.strip() for p in res.stdout.splitlines() if p.strip()]
        if ports:
            return "Ulangan COM/Serial qurilmalar (Arduino/CNC/Mikrokontroller):\n" + "\n".join([f"• {p}" for p in ports])
        return "Hozirda ulangan COM portli qurilmalar (Arduino/CNC) mavjud emas."
    except Exception as e:
        return f"COM portlarni tekshirishda xatolik: {e}"


def send_wake_on_lan(mac_address: str) -> str:
    """Tarmoqdagi boshqa kompyuter yoki smart qurilmani masofadan yoqish (Wake-on-LAN Magic Packet)"""
    try:
        cleaned_mac = mac_address.replace(":", "").replace("-", "").replace(".", "")
        if len(cleaned_mac) != 12:
            return f"Noto'g'ri MAC manzil: {mac_address}"
        
        data = bytes.fromhex("FF" * 6 + cleaned_mac * 16)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(data, ("255.255.255.255", 9))
        sock.close()
        return f"Wake-on-LAN signali {mac_address} qurilmasiga muvaffaqiyatli yuborildi."
    except Exception as e:
        return f"WoL yuborishda xatolik: {e}"


def phone_control(action: str = "status", target: str = "", text: str = "", ip: str = "", command: str = "") -> str:
    """Telefon va mobil qurilmalarni to'liq boshqarish (phone_controller moduliga yo'naltiradi)"""
    from actions.phone_controller import phone_controller
    return phone_controller(
        action=action,
        app_name=target or text,
        text=text or command,
        phone_number=target or text,
        ip=ip,
        query=command or text
    )


def device_controller(action: str = "scan_network", target: str = "", text: str = "", ip: str = "", mac: str = "", command: str = "") -> str:
    """Barcha tashqi qurilmalarni (Telefon, Tarmoq, Bluetooth, Arduino, Wake-on-LAN) boshqarish"""
    act = (action or "scan_network").lower().strip()

    if act in ["scan_network", "network", "wifi_devices", "tarmoq"]:
        return scan_network_devices()

    elif act in ["bluetooth", "bluetooth_devices", "bt"]:
        return list_bluetooth_devices()

    elif act in ["serial", "com_ports", "arduino", "cnc"]:
        return list_serial_com_ports()

    elif act in ["wake_on_lan", "wol", "wake"]:
        return send_wake_on_lan(mac or target)

    elif act in ["phone", "smartphone", "telegram_notify", "mobile"]:
        from actions.phone_controller import phone_controller
        return phone_controller(action=target or "status", app_name=text or command, text=text or command, ip=ip, query=command)

    else:
        from actions.phone_controller import phone_controller
        return phone_controller(action=act, app_name=target, text=text, ip=ip, query=command)
