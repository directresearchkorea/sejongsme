@echo off
echo.
echo ========================================
echo  Sejong SME Dashboard Web Deploy (GitHub)
echo ========================================
echo.

echo [1/3] Adding changes...
call git add .

echo [2/3] Committing changes...
call git commit -m "Auto-deploy: Update website data"

echo [3/3] Pushing to GitHub...
call git push origin master

echo.
echo ----------------------------------------
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Your website is successfully pushed to GitHub!
    echo Note: It may take 1-2 minutes for GitHub Pages to reflect changes online.
) else (
    echo [ERROR] Deployment failed. Ensure that you have an internet connection
    echo and GitHub authentication is set up.
)
echo ----------------------------------------
echo.
