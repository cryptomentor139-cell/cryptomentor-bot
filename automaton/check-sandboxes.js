// Check Conway sandboxes
const apiKey = "cnwy_k_HeT-F6vsVC_z6pmhYbBOyo1UJHtFhXyr";
const apiUrl = "https://api.conway.tech";

async function checkSandboxes() {
  try {
    console.log(`\n=== Checking Conway Sandboxes ===`);
    console.log(`API Key: ${apiKey.slice(0, 10)}...${apiKey.slice(-10)}\n`);

    const resp = await fetch(`${apiUrl}/v1/sandboxes`, {
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
    const sandboxes = Array.isArray(data) ? data : data.sandboxes || [];

    if (sandboxes.length === 0) {
      console.log(`❌ No sandboxes found`);
      console.log(`\nTo create a sandbox, you need Conway Credits.`);
      console.log(`Sandbox costs approximately $0.05-0.10 per hour depending on size.\n`);
    } else {
      console.log(`✅ Found ${sandboxes.length} sandbox(es):\n`);
      sandboxes.forEach((s, i) => {
        console.log(`${i + 1}. Sandbox ID: ${s.id || s.sandbox_id}`);
        console.log(`   Status: ${s.status || 'unknown'}`);
        console.log(`   Region: ${s.region || 'unknown'}`);
        console.log(`   vCPU: ${s.vcpu || 0}, Memory: ${s.memory_mb || 0}MB, Disk: ${s.disk_gb || 0}GB`);
        console.log(`   Created: ${s.created_at || 'unknown'}\n`);
      });
    }

    console.log(`===================================\n`);
  } catch (err) {
    console.error(`Failed to check sandboxes: ${err.message}`);
  }
}

checkSandboxes();
