import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";
import "@nomicfoundation/hardhat-verify";


const config: HardhatUserConfig = {
  solidity: {
    version: "0.8.28", 
    settings: {
      optimizer: {
        enabled: true,
        runs: 200,
      },
    },
  },
  networks: {
    polygon: {
      url: "https://polygon-mainnet.alchemy.com/v2/CzZJ3vpdWWnM9gNMTZj_tTwghXRRrGtr",
      accounts: [""],
      gasPrice: 50_000_000_000, 
      timeout: 100000,          
    },
  },
  
etherscan: {
  apiKey: {
    polygon: "",
  },
},
};

export default config;
