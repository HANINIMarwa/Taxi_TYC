@echo off
echo ===============================
echo 🚀 Configuration du Backend
echo ===============================

REM Étape 1 : Vérifier Python
where python >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo ❌ Python n'est pas trouvé dans le PATH.
    echo 👉 Vérifie ton installation ou ajoute Python manuellement.
    pause
    exit /b
)

REM Étape 2 : Créer un environnement virtuel
echo ✅ Python détecté.
python -m venv venv
call venv\Scripts\activate

REM Étape 3 : Mettre pip à jour
echo 📦 Mise à jour de pip...
python -m pip install --upgrade pip

REM Étape 4 : Installer les dépendances
echo 📥 Installation des dépendances...
python -m pip install -r requirements.txt

REM Étape 5 : Lancer le serveur FastAPI
echo 🚀 Lancement de FastAPI...
python -m uvicorn main:app --reload --port 8000
