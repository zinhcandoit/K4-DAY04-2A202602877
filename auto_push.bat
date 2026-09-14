@echo off
chcp 65001 >nul
cd /d C:\Users\Admin\K4-DAY04-2A202602877
echo === TỰ ĐỘNG ĐẨY CODE LÊN NHÁNH wrong_arg_value ===
echo.

git config --global user.email "hoangngoc12022004@gmail.com"
git config --global user.name "Ngocngoc12"

git fetch origin
git checkout -b wrong_arg_value 2>nul
git checkout wrong_arg_value

git add starter_v0/data/eval_group.json 
git add starter_v0/artifacts/REPORT.md 
git add starter_v0/artifacts/version_log.csv 
git add starter_v0/runs/

git commit -m "feat: bo sung test case wrong_arg_value va cap nhat ket qua eval"
git push -u origin wrong_arg_value

echo.
echo === HOÀN TẤT! HÃY KIỂM TRA LẠI TRÊN GITHUB ===
pause
