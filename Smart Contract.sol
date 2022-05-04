pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";


// Allow to split the balance through complex rules
interface Split{
    function getAddressAndAmountToSplit() view external returns(address, uint);
}

// MyBank contract
// This contract allows anyone to store any ERC20 tokens
contract MyBank {
    using SafeMath for unit256;
    
    // (token => user => amount)
    mapping (address => mapping(address => uint)) public userBalance;

    // Deposit ERC20 tokens to the contracts
    // The user must approve the bank before calling addToBalance
    function addToBalance(IERC20 token, uint amount) external
    {
        userBalance[address(token)][msg.sender] = userBalance[address(token)[msg.sender].add(amount);
        if(!token.transferFrom(msg.sender, address(this), amount)){
           revert("addToBalance failed.");
        }
    }

    // Withdraw part of the balance
    function withdrawBalance(IERC20 token) external
    {
        userBalance[address(token)][msg.sender] = 0;
        if(!token.transfer(msg.sender, userBalance[address(token)][msg.sender])){
           revert("withdrawBalance failed.");
        }
    }
    
    // Split the balance into two accounts
    // The usage of a Split contract allows to create complex split strategies
    function splitBalance(IERC20 token, Split split) external
    {
        require(split != Split(address(0x0)));
        uint balance = userBalance[address(token)][msg.sender];
        
        (address dest, uint amount) = Split(split).getAddressAndAmountToSplit();
        
        userBalance[address(token)][dest] = amount;
        userBalance[address(token)][msg.sender] = balance.sub(amount);
    }
}
