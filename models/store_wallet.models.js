"use strict";

const ERRORS = require("../error.js");
const db = require("../schemas");
const Security = require("./security.models.js");
const config = require('config');
const SERVER_CFG = config.get("SERVER");
const KEY = SERVER_CFG.api.KEY;
let logger = require("../logger");

let Wallet = db.wallets;

module.exports = async (user, platform, result) => {
    let security = new Security(KEY);

    const platform_name = platform.name.toLowerCase()

    if (platform_name == "gmail") {
        logger.debug(`Storing ${platform_name} wallet for ${user.id} ...`);

        await Wallet.create({
            userId: user.id,
            platformId: platform.id,
            username: security.encrypt(JSON.stringify(result.profile.data.name)).e_info,
            token: security.encrypt(JSON.stringify(result.token)).e_info,
            uniqueId: security.encrypt(JSON.stringify(result.profile.data.email)).e_info,
            uniqueIdHash: security.hash(result.profile.data.email),
            iv: security.iv
        }).catch(error => {
            logger.error("ERROR CREATING GMAIL WALLET");
            if (error.name == "SequelizeUniqueConstraintError") {
                if (error.original.code == "ER_DUP_ENTRY") {
                    logger.error("GMAIL WALLET RECORD EXIST ALREADY");
                    throw new ERRORS.Conflict();
                };
            };

            throw new ERRORS.InternalServerError(error);
        });

        logger.info("SUCCESSFULLY STORED GMAIL WALLET");
        return true;
    };

    if (platform_name == "twitter") {
        logger.debug(`Storing ${platform_name} wallet for ${user.id} ...`);

        await Wallet.create({
            userId: user.id,
            platformId: platform.id,
            username: security.encrypt(JSON.stringify(result.profile.name)).e_info,
            token: security.encrypt(JSON.stringify(result.token)).e_info,
            uniqueId: security.encrypt(JSON.stringify(result.profile.screen_name)).e_info,
            uniqueIdHash: security.hash(result.profile.screen_name),
            iv: security.iv
        }).catch(error => {
            logger.error("ERROR CREATING TWITTER WALLET");
            if (error.name == "SequelizeUniqueConstraintError") {
                if (error.original.code == "ER_DUP_ENTRY") {
                    logger.error("TWITTER WALLET RECORD EXIST ALREADY");
                    throw new ERRORS.Conflict();
                };
            };

            throw new ERRORS.InternalServerError(error);
        });

        logger.info("SUCCESSFULLY STORED TWITTER WALLET");
        return true;
    };

    if (platform_name == "telegram") {
        logger.debug(`Storing ${platform_name} wallet for ${user.id} ...`);

        await Wallet.create({
            userId: user.id,
            platformId: platform.id,
            token: security.encrypt(JSON.stringify(result)).e_info,
            uniqueId: security.encrypt(JSON.stringify(result)).e_info,
            uniqueIdHash: security.hash(result),
            iv: security.iv
        }).catch(error => {
            logger.error("ERROR CREATING TELEGRAM WALLET");
            if (error.name == "SequelizeUniqueConstraintError") {
                if (error.original.code == "ER_DUP_ENTRY") {
                    logger.error("TELEGRAM WALLET RECORD EXIST ALREADY");
                    throw new ERRORS.Conflict();
                };
            };

            throw new ERRORS.InternalServerError(error);
        });

        logger.info("SUCCESSFULLY STORED TELEGRAM WALLET");
        return true;
    };

    logger.error("PLATFORM NOT FOUND");
    throw new ERRORS.NotFound();
}