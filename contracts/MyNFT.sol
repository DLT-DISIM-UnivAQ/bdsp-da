// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract MyNFT is ERC721URIStorage, Ownable {
    uint256 private _tokenIds;

    constructor() ERC721("EngineerNFT", "ENGNFT") Ownable(msg.sender) {} 

    function mint(address recipient, string memory tokenURI) public onlyOwner returns (uint256) {
        uint256 newTokenId = _tokenIds;
        _mint(recipient, newTokenId);
        _setTokenURI(newTokenId, tokenURI);
        _tokenIds += 1;
        return newTokenId;
    }

    function getLatestTokenId() public view returns (uint256) {
        return _tokenIds == 0 ? 0 : _tokenIds - 1;
    }
}
