/**
 * Test script for formatHelpMessage function
 * Tests task 3.3.2: Create help message content
 */

import { formatHelpMessage } from './index.js';

console.log('Testing formatHelpMessage function...\n');
console.log('='.repeat(80));

try {
  const helpMessage = formatHelpMessage();
  
  console.log('\n✅ Help message generated successfully!\n');
  console.log('Message content:');
  console.log('-'.repeat(80));
  console.log(helpMessage);
  console.log('-'.repeat(80));
  
  // Verify all required components are present
  const checks = [
    { name: 'Contains /start command', test: helpMessage.includes('/start') },
    { name: 'Contains /status command', test: helpMessage.includes('/status') },
    { name: 'Contains /talk command', test: helpMessage.includes('/talk') },
    { name: 'Contains /help command', test: helpMessage.includes('/help') },
    { name: 'Contains usage examples', test: helpMessage.includes('_Example:_') },
    { name: 'Contains notification schedule', test: helpMessage.includes('08:00 WIB') && helpMessage.includes('14:00 WIB') && helpMessage.includes('20:00 WIB') },
    { name: 'Contains credit system explanation', test: helpMessage.includes('Credit System') && helpMessage.includes('credits') },
    { name: 'Contains tips section', test: helpMessage.includes('Tips:') },
    { name: 'Uses Markdown formatting', test: helpMessage.includes('*') && helpMessage.includes('_') },
    { name: 'Uses emojis', test: /[\u{1F300}-\u{1F9FF}]/u.test(helpMessage) }
  ];
  
  console.log('\n✅ Verification checks:');
  let allPassed = true;
  checks.forEach(check => {
    const status = check.test ? '✅' : '❌';
    console.log(`${status} ${check.name}`);
    if (!check.test) allPassed = false;
  });
  
  console.log('\n' + '='.repeat(80));
  if (allPassed) {
    console.log('✅ All checks passed! Help message is complete.');
  } else {
    console.log('❌ Some checks failed. Please review the help message.');
  }
  
} catch (error) {
  console.error('❌ Error testing formatHelpMessage:', error.message);
  console.error(error.stack);
  process.exit(1);
}
