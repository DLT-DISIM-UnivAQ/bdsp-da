// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";

contract MyNFT is ERC721URIStorage {
    uint256 private _tokenIds;

    event NFTMinted(address indexed recipient, uint256 tokenId, string tokenURI, string purpose);

    constructor() ERC721("BuildingLedgerDossier", "BDNFT") {}

    function mint(address recipient, string memory tokenURI, string memory purpose) public returns (uint256) {
        uint256 newTokenId = _tokenIds;
        _mint(recipient, newTokenId);
        _setTokenURI(newTokenId, tokenURI);
        _tokenIds += 1;

        emit NFTMinted(recipient, newTokenId, tokenURI, purpose);
        return newTokenId;
    }

    function getLatestTokenId() public view returns (uint256) {
        return _tokenIds == 0 ? 0 : _tokenIds - 1;
    }
}
