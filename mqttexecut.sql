-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Hôte : localhost
-- Généré le : mer. 25 août 2021 à 15:54
-- Version du serveur : 10.3.29-MariaDB-0+deb10u1
-- Version de PHP : 7.3.27-1~deb10u1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `bbd_projet`
--

-- --------------------------------------------------------

--
-- Structure de la table `mqttexecut`
--

CREATE TABLE `mqttexecut` (
  `id` int(11) NOT NULL,
  `code_in` varchar(50) DEFAULT NULL,
  `code_ex` varchar(50) DEFAULT NULL,
  `topic_in` varchar(255) DEFAULT NULL,
  `topic_ex` varchar(255) DEFAULT NULL,
  `client_id_in` int(11) DEFAULT NULL,
  `client_id_ex` int(11) DEFAULT NULL,
  `condition` mediumtext DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Déchargement des données de la table `mqttexecut`
--

INSERT INTO `mqttexecut` (`id`, `code_in`, `code_ex`, `topic_in`, `topic_ex`, `client_id_in`, `client_id_ex`, `condition`) VALUES
(1, '200', '200', 'prise', 'eclairage', 1, 2, '{   \"humiditte\":{     \"condition\":\"<\",     \"value\":\"21\"   } }');

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `mqttexecut`
--
ALTER TABLE `mqttexecut`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `mqttexecut`
--
ALTER TABLE `mqttexecut`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
