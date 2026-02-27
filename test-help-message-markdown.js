/**
 * Test: Verify formatHelpMessage() uses proper Telegram Markdown formatting
 * Task 3.3.3: Format help message with Markdown
 */

import { formatHelpMessage } from './index.js';

console.log('Testing formatHelpMessage() Markdown formatting...\n');

const helpMessage = formatHelpMessage();

// Verify the message is not empty
console.log('✓ Message is not empty:', helpMessage.length > 0);

// Verify bold text formatting with *text*
const hasBoldFormatting = helpMessage.includes('*CryptoMentor Help Guide*') &&
                          helpMessage.includes('*Available Commands:*') &&
                          helpMessage.includes('*/start*') &&
                          helpMessage.includes('*/status*') &&
                          helpMessage.includes('*/talk <message>*') &&
                          helpMessage.includes('*/help*') &&
                          helpMessage.includes('*Scheduled Notifications*') &&
                          helpMessage.includes('*Credit System*') &&
                          helpMessage.includes('*Tips:*');
console.log('✓ Has bold formatting with *text*:', hasBoldFormatting);

// Verify italic text formatting with _text_
const hasItalicFormatting = helpMessage.includes('_Example:_');
console.log('✓ Has italic formatting with _text_:', hasItalicFormatting);

// Verify proper line breaks with \n
const hasLineBreaks = helpMessage.includes('\n\n');
console.log('✓ Has proper line breaks with \\n:', hasLineBreaks);

// Verify emojis for visual appeal
const hasEmojis = helpMessage.includes('📚') &&
                  helpMessage.includes('🚀') &&
                  helpMessage.includes('📊') &&
                  helpMessage.includes('💬') &&
                  helpMessage.includes('❓') &&
                  helpMessage.includes('🔔') &&
                  helpMessage.includes('💰') &&
                  helpMessage.includes('💡');
console.log('✓ Has emojis for visual appeal:', hasEmojis);

// Verify structured sections with separators
const hasSeparators = helpMessage.includes('━━━━━━━━━━━━━━━━━━━━');
console.log('✓ Has structured sections with separators:', hasSeparators);

// Verify bullet points
const hasBulletPoints = helpMessage.includes('• ');
console.log('✓ Has bullet points:', hasBulletPoints);

// Display the formatted message
console.log('\n' + '='.repeat(50));
console.log('FORMATTED HELP MESSAGE:');
console.log('='.repeat(50) + '\n');
console.log(helpMessage);
console.log('\n' + '='.repeat(50));

// Summary
const allChecks = hasBoldFormatting && hasItalicFormatting && hasLineBreaks && 
                  hasEmojis && hasSeparators && hasBulletPoints;

if (allChecks) {
  console.log('\n✅ All Markdown formatting checks PASSED!');
  console.log('The formatHelpMessage() function uses proper Telegram Markdown formatting:');
  console.log('  • Bold text with *text*');
  console.log('  • Italic text with _text_');
  console.log('  • Proper line breaks with \\n');
  console.log('  • Emojis for visual appeal');
  console.log('  • Structured sections with separators');
  console.log('  • Bullet points for lists');
} else {
  console.log('\n❌ Some Markdown formatting checks FAILED!');
  process.exit(1);
}
