-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Hôte : localhost
-- Généré le : dim. 26 sep. 2021 à 20:12
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
-- Structure de la table `mqttcache`
--

CREATE TABLE `mqttcache` (
  `id` int(11) NOT NULL,
  `id_topic` int(11) NOT NULL,
  `id_client` int(11) NOT NULL,
  `ressult` mediumtext NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Déchargement des données de la table `mqttcache`
--

INSERT INTO `mqttcache` (`id`, `id_topic`, `id_client`, `ressult`) VALUES
(1, 2, 1, '200;mqtt_Temps_Salon;{\"Temps\": \"20\",\"humiditte\" : \"80\"}'),
(2, 2, 2, '200;mqtt_Temps_Salon;{\"Temps\": \"20\",\"humiditte\" : \"80\"}'),
(3, 2, 3, '201;interrre;{\"Button_2\": 1}');

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
(2, 'mqtt_test1', 0, '7894561230'),
(3, 'interrre', 1, '4563210789'),
(4, 'lumiere', 1, '15963247804'),
(7, 'price_1', 0, '1234567895'),
(9, 'prise_13', 0, '7879495613'),
(41, 'prise_12', 0, '12345678951');

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
  `condition` mediumtext DEFAULT NULL,
  `function` mediumtext DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Déchargement des données de la table `mqttexecut`
--

INSERT INTO `mqttexecut` (`id`, `code_in`, `code_ex`, `topic_in`, `topic_ex`, `client_id_in`, `client_id_ex`, `condition`, `function`) VALUES
(1, '200', '200', 'prise', 'eclairage', 1, 2, '{   \"humiditte\":{     \"condition\":\"<\",     \"value\":\"21\"   } }', '{\"function\": {\"swich\": {\"value\": false}}}'),
(2, '200', '200', 'prise', 'eclairage', 3, 2, '{   \"Button_1\":{     \"condition\":\"==\",     \"value\":\"1\",     \"objet\" : \"led_1\"} }', '{\"function\": {\"swich\": {\"value\": false}}}'),
(3, '200', '200', 'prise', NULL, 3, 4, '{   \"Button_1\":{     \"condition\":\"==\",     \"value\":\"1\",     \"objet\" : \"led_1\"} }', '{\"function\": {\"swich\": {\"value\": false}}}'),
(4, '201', '201', 'prise', 'eclairage', 3, 4, '{   \"Button_2\":{     \"condition\":\"==\",     \"value\":\"1\",     \"objet\" : \"led_2\"} }', '{\"function\": {\"swich\": {\"value\": true}}}'),
(5, '202', '202', 'prise', 'eclairage', 3, 3, '{   \"Button_3\":{     \"condition\":\"==\",     \"value\":\"1\",     \"objet\" : \"led_1\"} }', '{\"function\": {\"swich\": {\"value\": false}}}');

-- --------------------------------------------------------

--
-- Structure de la table `mqtttopic`
--

CREATE TABLE `mqtttopic` (
  `id_topic` int(11) NOT NULL,
  `topic` varchar(255) NOT NULL,
  `active` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Déchargement des données de la table `mqtttopic`
--

INSERT INTO `mqtttopic` (`id_topic`, `topic`, `active`) VALUES
(1, 'electriciter', 1),
(2, 'prise', 1),
(3, 'eleclairage', 1);

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `mqttcache`
--
ALTER TABLE `mqttcache`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `mqttclient`
--
ALTER TABLE `mqttclient`
  ADD PRIMARY KEY (`id_client`),
  ADD UNIQUE KEY `uid` (`uid`);

--
-- Index pour la table `mqttexecut`
--
ALTER TABLE `mqttexecut`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `mqtttopic`
--
ALTER TABLE `mqtttopic`
  ADD PRIMARY KEY (`id_topic`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `mqttcache`
--
ALTER TABLE `mqttcache`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT pour la table `mqttclient`
--
ALTER TABLE `mqttclient`
  MODIFY `id_client` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=42;

--
-- AUTO_INCREMENT pour la table `mqttexecut`
--
ALTER TABLE `mqttexecut`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT pour la table `mqtttopic`
--
ALTER TABLE `mqtttopic`
  MODIFY `id_topic` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
