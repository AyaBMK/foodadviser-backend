const express = require('express');
const userController = require('../controllers/userController');

const router = express.Router();

// Route pour l'inscription
router.post('/register', userController.register);

// Route pour la connexion
router.post('/login', userController.login);

module.exports = router;
