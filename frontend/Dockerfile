# frontend/Dockerfile

FROM node:18-alpine

# Define diretório de trabalho
WORKDIR /app

# Copia arquivos do projeto e instala dependências
COPY package.json package-lock.json ./
RUN npm install

# Copia o restante do código
COPY . .

# Comando padrão para ambiente de desenvolvimento
CMD ["npm", "run", "dev"]
