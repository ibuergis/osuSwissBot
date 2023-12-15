CREATE TABLE `osuUser` (
    `userId` INT UNSIGNED UNIQUE,
    `username` VARCHAR(100) NOT NULL,
    `osuRank` INT NOT NULL,
    `maniaRank` INT NOT NULL,
    `taikoRank` INT NOT NULL,
    `catchRank` INT NOT NULL,
    `country` VARCHAR(2) NOT NULL,
    PRIMARY KEY (`userId`)
);

DROP TABLE `player`;