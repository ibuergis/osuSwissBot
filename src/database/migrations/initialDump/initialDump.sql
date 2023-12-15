CREATE TABLE `player` (
    `id` INT UNSIGNED AUTO_INCREMENT,
    `userId` VARCHAR(100) UNIQUE,
    `username` VARCHAR(100),
    `rank` INT,
    PRIMARY KEY (`id`)
)

INSERT INTO `player` (`id`, `userId`, `username`, `rank`) VALUE
(1, 1, '1', 1);