#!/bin/bash
pyinstaller --onefile --add-data ../config/config.yaml:config --add-data ../resources:resources backend/main.py
