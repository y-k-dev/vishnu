-- データベース
CREATE DATABASE tradingbot;

-- テーブル
CREATE TABLE `entry` (`side` varchar(255) NOT NULL);

CREATE TABLE `ticker` (
    `date` timestamp NOT NULL,
    `best_bid` int unsigned NOT NULL,
    `best_ask` int unsigned NOT NULL
);

CREATE TABLE `backtest_entry` (
    `date` timestamp NOT NULL,
    `side` varchar(255) NOT NULL,
    `price` int unsigned NOT NULL,
    `size` float unsigned NOT NULL
);

commit;