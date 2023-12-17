CREATE TABLE `osuMentionDiscordUserOnGuild` (
    `id` INT UNSIGNED AUTO_INCREMENT,
    `discordUser` INT UNSIGNED NOT NULL,
    `guild` INT UNSIGNED NOT NULL,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`discordUser`) REFERENCES `discordUser`(`id`),
    FOREIGN KEY (`guild`) REFERENCES `guild`(`id`)
);

CREATE TABLE `maniaMentionDiscordUserOnGuild` (
    `id` INT UNSIGNED AUTO_INCREMENT,
    `discordUser` INT UNSIGNED NOT NULL,
    `guild` INT UNSIGNED NOT NULL,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`discordUser`) REFERENCES `discordUser`(`id`),
    FOREIGN KEY (`guild`) REFERENCES `guild`(`id`)
);

CREATE TABLE `taikoMentionDiscordUserOnGuild` (
    `id` INT UNSIGNED AUTO_INCREMENT,
    `discordUser` INT UNSIGNED NOT NULL,
    `guild` INT UNSIGNED NOT NULL,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`discordUser`) REFERENCES `discordUser`(`id`),
    FOREIGN KEY (`guild`) REFERENCES `guild`(`id`)
);

CREATE TABLE `catchMentionDiscordUserOnGuild` (
    `id` INT UNSIGNED AUTO_INCREMENT,
    `discordUser` INT UNSIGNED NOT NULL,
    `guild` INT UNSIGNED NOT NULL,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`discordUser`) REFERENCES `discordUser`(`id`),
    FOREIGN KEY (`guild`) REFERENCES `guild`(`id`)
);