#!/bin/bash

# Script de démarrage pour l'application Git Log Analyzer
# Ce script démarre le backend Flask et le frontend React

echo "🚀 Démarrage de l'application Git Log Analyzer"
echo "=============================================="

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour vérifier si une commande existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Vérification des prérequis
echo -e "${BLUE}🔍 Vérification des prérequis...${NC}"

if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 n'est pas installé${NC}"
    exit 1
fi

if ! command_exists node; then
    echo -e "${RED}❌ Node.js n'est pas installé${NC}"
    exit 1
fi

if ! command_exists npm; then
    echo -e "${RED}❌ npm n'est pas installé${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Tous les prérequis sont installés${NC}"

# Configuration du backend
echo -e "\n${BLUE}🔧 Configuration du backend Flask...${NC}"
cd backend

# Création de l'environnement virtuel s'il n'existe pas
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Création de l'environnement virtuel...${NC}"
    python3 -m venv venv
fi

# Activation de l'environnement virtuel
echo -e "${YELLOW}🔄 Activation de l'environnement virtuel...${NC}"
source venv/bin/activate

# Installation des dépendances
echo -e "${YELLOW}📥 Installation des dépendances Python...${NC}"
pip install -r requirements.txt

# Configuration du frontend
echo -e "\n${BLUE}🔧 Configuration du frontend React...${NC}"
cd ../frontend

# Installation des dépendances Node.js
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📥 Installation des dépendances Node.js...${NC}"
    npm install
fi

# Retour au répertoire principal
cd ..

# Création des fichiers .env s'ils n'existent pas
echo -e "\n${BLUE}⚙️  Configuration des variables d'environnement...${NC}"

if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}📝 Création du fichier .env pour le backend...${NC}"
    cp backend/.env.example backend/.env 2>/dev/null || echo "FLASK_ENV=development
PORT=5000
# GITHUB_TOKEN=your_github_token_here" > backend/.env
fi

if [ ! -f "frontend/.env" ]; then
    echo -e "${YELLOW}📝 Création du fichier .env pour le frontend...${NC}"
    echo "REACT_APP_API_URL=http://localhost:5000" > frontend/.env
fi

# Fonction pour démarrer le backend
start_backend() {
    echo -e "\n${GREEN}🔥 Démarrage du serveur Flask...${NC}"
    cd backend
    source venv/bin/activate
    export FLASK_ENV=development
    python app.py &
    BACKEND_PID=$!
    echo -e "${GREEN}✅ Backend démarré (PID: $BACKEND_PID)${NC}"
    cd ..
}

# Fonction pour démarrer le frontend
start_frontend() {
    echo -e "\n${GREEN}🎨 Démarrage de l'application React...${NC}"
    cd frontend
    npm start &
    FRONTEND_PID=$!
    echo -e "${GREEN}✅ Frontend démarré (PID: $FRONTEND_PID)${NC}"
    cd ..
}

# Fonction de nettoyage
cleanup() {
    echo -e "\n${YELLOW}🛑 Arrêt de l'application...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo -e "${GREEN}✅ Backend arrêté${NC}"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo -e "${GREEN}✅ Frontend arrêté${NC}"
    fi
    exit 0
}

# Configuration du signal d'arrêt
trap cleanup SIGINT SIGTERM

# Démarrage des services
start_backend
sleep 3  # Attendre que le backend soit prêt
start_frontend

echo -e "\n${GREEN}🎉 Application démarrée avec succès!${NC}"
echo -e "${BLUE}📍 Backend API: http://localhost:5000${NC}"
echo -e "${BLUE}📍 Frontend: http://localhost:3000${NC}"
echo -e "\n${YELLOW}💡 Conseil: Configurez votre GITHUB_TOKEN dans backend/.env pour éviter les limites de taux${NC}"
echo -e "${YELLOW}⏹️  Appuyez sur Ctrl+C pour arrêter l'application${NC}"

# Attendre indéfiniment
wait