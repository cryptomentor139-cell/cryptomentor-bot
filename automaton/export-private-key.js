// Export private key for importing to MetaMask
import fs from 'fs';
import path from 'path';

const WALLET_FILE = path.join(
  process.env.HOME || process.env.USERPROFILE || '/root',
  '.automaton',
  'wallet.json'
);

try {
  if (!fs.existsSync(WALLET_FILE)) {
    console.error('❌ Wallet file not found:', WALLET_FILE);
    process.exit(1);
  }

  const walletData = JSON.parse(fs.readFileSync(WALLET_FILE, 'utf-8'));
  
  console.log('\n🔑 AUTOMATON WALLET PRIVATE KEY\n');
  console.log('⚠️  KEEP THIS SECRET! Anyone with this key controls the wallet.\n');
  console.log('Private Key:', walletData.privateKey);
  console.log('\nCreated:', walletData.createdAt);
  console.log('\n📝 To import to MetaMask:');
  console.log('1. Open MetaMask');
  console.log('2. Click account icon → Import Account');
  console.log('3. Select "Private Key"');
  console.log('4. Paste the private key above');
  console.log('5. Click "Import"');
  console.log('\n✅ After import, you can use MetaMask to connect to Conway dashboard\n');
  
} catch (error) {
  console.error('Error reading wallet:', error.message);
  process.exit(1);
}
