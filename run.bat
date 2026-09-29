@echo off
chcp 65001 > nul
cd src
python main.py --vfs ../vfs_nested.json
pause