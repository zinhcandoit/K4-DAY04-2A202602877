@echo off
cd /d C:\Users\Admin\K4-DAY04-2A202602877\starter_v0
echo === Activating virtual environment ===
call .venv\Scripts\activate.bat
echo === Running eval_group.json (v4) ===
python run_eval.py --phase B --suite group --version v4 --provider gemini --eval-cases data/eval_group.json
echo.
echo === Done! Check the runs/ folder for output ===
pause
