-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Hôte : localhost
-- Généré le : mer. 25 août 2021 à 15:53
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
-- Structure de la table `mqttclient`
--

CREATE TABLE `mqttclient` (
  `id_client` int(11) NOT NULL,
  `client` varchar(255) NOT NULL,
  `is_alive` tinyint(1) NOT NULL,
  `uid` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Déchargement des données de la table `mqttclient`
--

INSERT INTO `mqttclient` (`id_client`, `client`, `is_alive`, `uid`) VALUES
(1, 'mqtt_Temps_Salon', 0, '1523698745'),
(2, 'mqtt_test1', 0, '7894561230');

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `mqttclient`
--
ALTER TABLE `mqttclient`
  ADD PRIMARY KEY (`id_client`),
  ADD UNIQUE KEY `uid` (`uid`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `mqttclient`
--
ALTER TABLE `mqttclient`
  MODIFY `id_client` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
