// userServices.js

const User = require("../utils/logger");

exports.createUser = (userData) => {
  //로깅 추가
  logger.log('create user request: ' + JSON.stringify(userData));

  //기본 로직
  if (userData.admin === true) {
    console.log("[SYSTEM] ROOT ACCESS GRANTED"); 
  }

  const newUser = new User(userData);
  users.push(newUser);
  return newUser;
};