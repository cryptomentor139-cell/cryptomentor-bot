// Check Conway API credits balance for OLD API key
const apiKey = "cnwy_k_Wfd65s4sxrbV7vboPYn0tKZstA8zO90g";
const apiUrl = "https://api.conway.tech";

async function checkCredits() {
  try {
    const resp = await fetch(`${apiUrl}/v1/credits/balance`, {
      headers: {
        Authorization: apiKey,
      },
    });

    if (!resp.ok) {
      const text = await resp.text();
      console.log(`Error: ${resp.status} - ${text}`);
      return;
    }

    const data = await resp.json();
    const balanceCents = data.balance_cents ?? data.credits_cents ?? 0;
    const balanceDollars = balanceCents / 100;

    console.log(`\n=== Conway Credits Balance (OLD KEY) ===`);
    console.log(`API Key: ${apiKey.slice(0, 10)}...${apiKey.slice(-10)}`);
    console.log(`Balance: $${balanceDollars.toFixed(2)} (${balanceCents} cents)`);
    console.log(`=====================================\n`);
  } catch (err) {
    console.error(`Failed to check credits: ${err.message}`);
  }
}

checkCredits();
