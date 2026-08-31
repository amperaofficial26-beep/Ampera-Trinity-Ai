# -*- coding: utf-8 -*-
"""Paket engine Ampera Trinity AI.

File ini WAJIB ada. Tanpa __init__.py, folder `engines/` diperlakukan
sebagai *namespace package*; bila terjadi error saat mengimpor salah satu
modul di dalamnya, Python 3.13+ menutupi error aslinya dan hanya
melempar `KeyError: 'engines.groq_engine'` sehingga penyebabnya sulit
dilacak.
"""
