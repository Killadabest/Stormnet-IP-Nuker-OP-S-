# STORMNET

> Educational network stress testing tool for authorized environments only.

## Description

STORMNET is a Python-based network utility designed for educational purposes and authorized penetration testing. It demonstrates concepts related to network traffic generation, socket programming, and distributed systems.

This tool was created to help students and security researchers understand how network flooding techniques work so they can better defend against them.

## Features

- Multi-vector traffic generation (HTTP, UDP, SYN)
- Proxy rotation support via free public proxy lists
- Real-time packet and bandwidth monitoring
- Adjustable rate limiting to prevent local network saturation
- Threaded architecture for concurrent connections
- Clean terminal interface

## Requirements

- Python 3.8+
- Linux / macOS / Windows
- Root/admin privileges for raw socket operations (SYN flood)
- Internet connection for proxy fetching
