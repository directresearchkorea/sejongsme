@echo off
echo.
echo ========================================
echo  Sejong SME Dashboard Web Deploy (GitHub)
echo ========================================
echo.

echo [1/2] Connecting to GitHub Pages...
echo.
echo IMPORTANT: If this is your first time deploying to GitHub Pages,
echo you might need to authenticate.
echo.

:: We use gh-pages node module to deploy the current directory to the gh-pages branch.
call npx.cmd -y gh-pages -d .

echo.
echo ----------------------------------------
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Your website is successfully deployed to GitHub Pages!
    echo Note: It may take 1-2 minutes for GitHub to build and reflect changes online.
) else (
    echo [ERROR] Deployment failed. Ensure that you have committed your files
    echo and set up a github remote repository origin first.
)
echo ----------------------------------------
echo.
pause
