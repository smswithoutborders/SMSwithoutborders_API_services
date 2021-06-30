module.exports = (sequelize, Sequelize) => {
    let Users = sequelize.define("users", {
        id: {
            type: Sequelize.STRING(64),
            defaultValue: Sequelize.UUIDV1,
            primaryKey: true
        },
        password: Sequelize.STRING,
        auth_key: {
            type: Sequelize.STRING,
            unique: true
        }
    });

    return Users;
}