# Einfaches Node.js Image nehmen
FROM node:18-alpine

# Setze Arbeitsverzeichnis
WORKDIR /app

# Kopiere nur die notwendigen Dateien
COPY package.json package-lock.json* ./

# Installiere Abhängigkeiten
RUN npm install --omit=dev

# Kopiere den Rest des Codes
COPY . .

# Starte den Server
CMD ["npm", "start"]

# Exponiere Port 3000
EXPOSE 3000
