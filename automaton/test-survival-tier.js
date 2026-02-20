// Test survival tier calculation with USDC
import { getSurvivalTier } from './dist/conway/credits.js';
import { getUsdcBalance } from './dist/conway/x402.js';

const WALLET_ADDRESS = '0x63116672BEf9F26FD906Cd2a57550F7A13925822';

async function test() {
  console.log('Testing survival tier calculation...\n');
  
  // Test 1: Check USDC balance
  console.log('1. Checking USDC balance...');
  try {
    const usdcBalance = await getUsdcBalance(WALLET_ADDRESS);
    console.log('   USDC Balance:', usdcBalance);
    console.log('   USDC in cents:', Math.floor(usdcBalance * 100));
  } catch (error) {
    console.error('   Error:', error.message);
  }
  
  // Test 2: Calculate tier with 0 credits but 10.5 USDC
  console.log('\n2. Testing getSurvivalTier(0, 10.5)...');
  const tier1 = getSurvivalTier(0, 10.5);
  console.log('   Result:', tier1);
  console.log('   Expected: "normal" (because 10.5 USDC = 1050 cents > 50 cents threshold)');
  
  // Test 3: Calculate tier with 0 credits and 0 USDC
  console.log('\n3. Testing getSurvivalTier(0, 0)...');
  const tier2 = getSurvivalTier(0, 0);
  console.log('   Result:', tier2);
  console.log('   Expected: "dead"');
  
  // Test 4: Calculate tier with 100 credits and 0 USDC
  console.log('\n4. Testing getSurvivalTier(100, 0)...');
  const tier3 = getSurvivalTier(100, 0);
  console.log('   Result:', tier3);
  console.log('   Expected: "normal"');
}

test().catch(console.error);
