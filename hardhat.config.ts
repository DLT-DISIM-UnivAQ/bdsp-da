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
      url: "https://polygon-mainnet.g.alchemy.com/v2/CzZJ3vpdWWnM9gNMTZj_tTwghXRRrGtr",
      accounts: ["cec0c36752a19d30639c58e472d75a39b0f11c6470a1e8015f184947aa22f697"],
      gasPrice: 50_000_000_000, 
      timeout: 100000,          
    },
  },
  
etherscan: {
  apiKey: {
    polygon: "4FP4IG6XMJZRHGAU71WGT7Q6QG46Z5C39U",
  },
},
};

export default config;
