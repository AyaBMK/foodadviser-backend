const express = require('express');
const userRoutes = require('./routes/userRoutes');
const dotenv = require('dotenv');

// Charger les variables d'environnement depuis le fichier .env
dotenv.config();

const app = express();

// Middleware pour parser le corps des requêtes en JSON
app.use(express.json());

// Routes utilisateur
app.use('/api/users', userRoutes);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
