// Quick script to check USDC balance on Base
import { createPublicClient, http, formatUnits } from 'viem';
import { base } from 'viem/chains';

const USDC_ADDRESS = '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913';
const WALLET_ADDRESS = '0x63116672BEf9F26FD906Cd2a57550F7A13925822';

const BALANCE_OF_ABI = [
  {
    inputs: [{ name: 'account', type: 'address' }],
    name: 'balanceOf',
    outputs: [{ name: '', type: 'uint256' }],
    stateMutability: 'view',
    type: 'function',
  },
];

const client = createPublicClient({
  chain: base,
  transport: http(),
});

async function checkBalance() {
  try {
    console.log('Checking USDC balance on Base...');
    console.log('Wallet:', WALLET_ADDRESS);
    
    const balance = await client.readContract({
      address: USDC_ADDRESS,
      abi: BALANCE_OF_ABI,
      functionName: 'balanceOf',
      args: [WALLET_ADDRESS],
    });
    
    const usdcBalance = formatUnits(balance, 6); // USDC has 6 decimals
    
    console.log('\n✅ Balance:', usdcBalance, 'USDC');
    console.log('Raw balance:', balance.toString());
    
    if (parseFloat(usdcBalance) > 0) {
      console.log('\n🎉 Automaton is funded! Ready to run!');
    } else {
      console.log('\n⚠️  No USDC found. Transaction might still be pending...');
    }
  } catch (error) {
    console.error('Error checking balance:', error.message);
  }
}

checkBalance();
