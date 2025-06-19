
-- Table: roles
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(50) UNIQUE NOT NULL
);

INSERT INTO roles (id, nom) VALUES
(2, 'achat'),
(4, 'gerant'),
(9, 'livreur'),
(1, 'owner'),
(3, 'reparation');

-- Table: users
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role_id INTEGER REFERENCES roles(id),
    actif BOOLEAN DEFAULT TRUE,
    telephone VARCHAR(8)
);

INSERT INTO users (id, username, password, role_id, actif, telephone) VALUES
(5, 'test', '9af15b336e6a9619928537df30b2e6a2376569fcf9d7e773eccede65606529a0', 3, TRUE, '55989789'),
(6, 'Hedi', '8e1f192fe25ad49be764c3f55c68beb32f7aa66f85344e026b76cfaaa1d3d88a', 1, TRUE, '99511502'),
(7, 'Hassen', '3c2ea00c905c2d6de9299763ef81e9363a12f4ef5f0c7ff0a550a5b33d5df13a', 4, TRUE, '97865964'),
(8, 'Nouha', 'b281bc2c616cb3c3a097215fdc9397ae87e6e06b156cc34e656be7a1a9ce8839', 2, TRUE, '99887788'),
(9, 'Saddem', '8c9a013ab70c0434313e3e881c310b9ff24aff1075255ceede3f2c239c231623', 3, TRUE, '26998887'),
(12, 'testrole', '02023546b4039abe3b9f355c23dafd9119570f301a024e2fd2ff3186ae54060c', 9, TRUE, '65587894'),
(13, 'rehzbe', '02023546b4039abe3b9f355c23dafd9119570f301a024e2fd2ff3186ae54060c', 9, TRUE, '65587894');

-- Table: reparations
CREATE TABLE IF NOT EXISTS reparations (
    id SERIAL PRIMARY KEY,
    code_reparation VARCHAR(50) UNIQUE,
    type_appareil VARCHAR(50),
    os VARCHAR(50),
    panne TEXT,
    modele VARCHAR(100),
    montant_total DECIMAL(10,2),
    acompte DECIMAL(10,2),
    paiement_effectue BOOLEAN,
    type_paiement VARCHAR(50),
    date_enregistrement TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    statut VARCHAR(50) DEFAULT 'En attente',
    numero_tel VARCHAR(20)
);

INSERT INTO reparations (id, code_reparation, type_appareil, os, panne, modele, montant_total, acompte, paiement_effectue, type_paiement, date_enregistrement, statut, numero_tel) VALUES
(3, 'R-0000003', 'Téléphone', 'iOS', 'afficheur ', 'iphone 13', 102.00, 10.00, TRUE, 'Virement', '2025-06-13 19:24:50', 'En cours de réparation', '55897883'),
(7, 'R-0000007', 'Téléphone', 'Android', 'panne afficheur', 'TEST HEDI', 30.00, 0.00, TRUE, 'Espèces', '2025-06-15 12:10:45', 'En attente', '33666555'),
(11, 'R-0000011', 'PC', 'Linux', 'changement stockage', 'iphone 7', 245.00, 0.00, FALSE, 'Autre', '2025-06-16 22:38:52', 'En attente', '99886998'),
(13, 'R-0000013', 'Tablette', 'Android', 'test bum tel ', 'test bum tel', 22.00, 0.00, TRUE, 'Espèces', '2025-06-16 22:46:45', 'En attente', 'pzpzp'),
(14, 'R-0000014', 'Téléphone', 'Android', 'test 2num tel', 'test 2num tel', 0.00, 0.00, TRUE, 'Espèces', '2025-06-16 22:48:37', 'En attente', 'test 2num tel');

-- Table: achats (corrigé uniquement avec reparation_id existants)
CREATE TABLE IF NOT EXISTS achats (
    id SERIAL PRIMARY KEY,
    reparation_id INTEGER REFERENCES reparations(id) ON DELETE CASCADE,
    libelle VARCHAR(255),
    montant DECIMAL(10,2),
    date_achat TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO achats (reparation_id, libelle, montant, date_achat) VALUES
(7, 'afficheur log', 10.00, '2025-06-15 11:12:02'),
(7, 'micro', 1.00, '2025-06-15 17:52:39');

-- Table: logs (structure uniquement, sans données pour éviter erreurs)
CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    utilisateur VARCHAR(100) NOT NULL,
    action_type VARCHAR(20) NOT NULL,
    target_type VARCHAR(20) NOT NULL,
    detail TEXT,
    date_action TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
