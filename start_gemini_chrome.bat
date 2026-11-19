@echo off
rem Separate Chrome window for Claude automation (own profile, debug port 9333)
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9333 --user-data-dir=C:\Users\user\chrome-gemini-bot --no-first-run https://gemini.google.com/app
