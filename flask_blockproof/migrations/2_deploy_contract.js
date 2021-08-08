const SaveTransaction = artifacts.require("SaveTransaction");

module.exports = function (deployer) {
  deployer.deploy(SaveTransaction);
};
