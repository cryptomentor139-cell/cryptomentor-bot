// Check Conway API credits balance
const CONWAY_API_URL = 'https://api.conway.tech';
const CONWAY_API_KEY = 'cnwy_k_HeT-F6vsVC_z6pmhYbBOyo1UJHtFhXyr';

async function checkCredits() {
  try {
    console.log('Checking Conway API credits...\n');
    
    const response = await fetch(`${CONWAY_API_URL}/v1/credits/balance`, {
      method: 'GET',
      headers: {
        'Authorization': CONWAY_API_KEY,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      const text = await response.text();
      console.error('❌ Error:', response.status, text);
      return;
    }
    
    const data = await response.json();
    const balanceCents = data.balance_cents || data.credits_cents || 0;
    const balanceDollars = (balanceCents / 100).toFixed(2);
    
    console.log('✅ Conway API Credits Balance:', `$${balanceDollars}`);
    console.log('Raw balance (cents):', balanceCents);
    
    if (balanceCents > 0) {
      console.log('\n💡 You can transfer credits to automaton wallet:');
      console.log('   To: 0x63116672BEf9F26FD906Cd2a57550F7A13925822');
      console.log('   Amount: Up to', balanceCents, 'cents');
    } else {
      console.log('\n⚠️  No credits in this API key account.');
      console.log('   You need to buy credits first via Conway platform.');
    }
    
  } catch (error) {
    console.error('Error:', error.message);
  }
}

checkCredits();
