@echo off
cd /d %~dp0
py execution\send_weekly_summary.py
exit
