CREATE TABLE `guild` (
    `id` INT UNSIGNED AUTO_INCREMENT,
    `guildId` VARCHAR(100) UNIQUE NOT NULL,
    `osuScoresChannel` VARCHAR(100),
    `maniaScoresChannel` VARCHAR(100),
    `taikoScoresChannel` VARCHAR(100),
    `catchScoresChannel` VARCHAR(100),
    PRIMARY KEY (`id`)
);

CREATE TABLE `discordUser` (
    `id` INT UNSIGNED AUTO_INCREMENT,
    `userId` VARCHAR(100) UNIQUE NOT NULL,
    PRIMARY KEY (`id`)
);

