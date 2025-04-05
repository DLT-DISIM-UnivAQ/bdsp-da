import { ethers } from "hardhat";

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deploying from:", deployer.address);

  const NFT = await ethers.getContractFactory("MyNFT");
  const nft = await NFT.deploy();

  await nft.waitForDeployment(); 
  const contractAddress = await nft.getAddress();

  console.log("✅ NFT contract deployed at:", contractAddress);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
