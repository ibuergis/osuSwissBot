CREATE TABLE `osuUser` (
    `id` INT UNSIGNED UNIQUE,
    `username` VARCHAR(100) NOT NULL,
    `osuRank` INT,
    `maniaRank` INT,
    `taikoRank` INT,
    `catchRank` INT,
    `country` VARCHAR(2) NOT NULL,
    PRIMARY KEY (`id`)
);

DROP TABLE `player`;