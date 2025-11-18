const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying contracts with account:", deployer.address);
  
  const RecipeNFT = await hre.ethers.getContractFactory("RecipeNFT");
  const recipeNft = await RecipeNFT.deploy();
  await recipeNft.waitForDeployment();

  console.log("RecipeNFT deployed to:", await recipeNft.getAddress());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});

