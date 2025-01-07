const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const pool = require('../database/db');

module.exports = {
    // Inscription d'un utilisateur
    register: async (req, res) => {
        const { email, pseudo, password, passwordConfirmation, birthdate } = req.body;

        if (password !== passwordConfirmation) {
            return res.status(400).json({ error: "Passwords do not match" });
        }

        if (!birthdate) {
            return res.status(400).json({ error: "Birthdate is required" });
        }

        try {
            // Vérifier si l'email ou le pseudo existe déjà
            const emailCheck = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
            const pseudoCheck = await pool.query('SELECT * FROM users WHERE pseudo = $1', [pseudo]);

            if (emailCheck.rows.length > 0) {
                return res.status(400).json({ error: "Email already in use" });
            }

            if (pseudoCheck.rows.length > 0) {
                return res.status(400).json({ error: "Pseudo already in use" });
            }

            // Hachage du mot de passe
            const hashedPassword = await bcrypt.hash(password, 10);

            // Insertion dans la base de données
            const result = await pool.query(
                'INSERT INTO users (email, pseudo, password_hash, birthdate) VALUES ($1, $2, $3, $4) RETURNING *',
                [email, pseudo, hashedPassword, birthdate]
            );

            const user = result.rows[0];
            res.status(201).json({ message: 'User created successfully', userId: user.id });
        } catch (error) {
            console.error(error);
            res.status(500).json({ error: 'Internal Server Error' });
        }
    },

    // Connexion d'un utilisateur
    login: async (req, res) => {
        const { emailOrPseudo, password } = req.body;

        try {
            const userQuery = await pool.query(
                'SELECT * FROM users WHERE email = $1 OR pseudo = $2',
                [emailOrPseudo, emailOrPseudo]
            );

            if (userQuery.rows.length === 0) {
                return res.status(400).json({ error: 'Invalid email or pseudo' });
            }

            const user = userQuery.rows[0];

            // Vérification du mot de passe
            const passwordMatch = await bcrypt.compare(password, user.password_hash);

            if (!passwordMatch) {
                return res.status(400).json({ error: 'Invalid password' });
            }

            // Génération du token JWT
            const token = jwt.sign({ userId: user.id }, process.env.JWT_SECRET, { expiresIn: '1h' });

            res.status(200).json({ message: 'Login successful', token });
        } catch (error) {
            console.error(error);
            res.status(500).json({ error: 'Internal Server Error' });
        }
    }
};
