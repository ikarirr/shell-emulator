@echo off
chcp 65001 > nul
cd src
python main.py --vfs ../vfs_nested.json --script ../scripts/test_mv.txt
pause