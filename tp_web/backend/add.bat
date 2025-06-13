@echo off
setlocal

echo ===============================
echo ⚙️ Ajout de Python au PATH
echo ===============================

REM Définir les chemins Python
set PYTHON_DIR=C:\Python310
set PYTHON_SCRIPTS=C:\Python310\Scripts

REM Ajouter à la variable PATH utilisateur
echo ➕ Ajout de %PYTHON_DIR% au PATH utilisateur...
setx PATH "%PATH%;%PYTHON_DIR%;%PYTHON_SCRIPTS%" /M

echo ✅ Python a été ajouté au PATH système.
echo 🔁 Redémarre ton terminal pour que les changements prennent effet.

REM Test rapide
echo.
echo ➤ Vérification :
%PYTHON_DIR%\python310.exe --version

pause
endlocal
