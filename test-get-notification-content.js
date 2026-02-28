import { AutomatonAPIClient } from './index.js';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

/**
 * Test script for getNotificationContent() method
 * Tests task 2.2.5: Implement getNotificationContent() method
 */

async function testGetNotificationContent() {
  console.log('='.repeat(80));
  console.log('Testing getNotificationContent() Method');
  console.log('='.repeat(80));
  console.log();

  try {
    // Create API client instance
    const apiClient = new AutomatonAPIClient();
    console.log('✅ API client created successfully\n');

    // Test: Get notification content
    console.log('Test: Fetching notification content from API...');
    console.log('-'.repeat(80));
    
    const notificationData = await apiClient.getNotificationContent();
    
    console.log('\n📋 Notification Data Received:');
    console.log(JSON.stringify(notificationData, null, 2));
    
    // Validate response structure
    console.log('\n🔍 Validating Response Structure:');
    
    if (notificationData.content) {
      console.log('✅ Content field exists');
      console.log(`   Content: "${notificationData.content.substring(0, 100)}${notificationData.content.length > 100 ? '...' : ''}"`);
    } else {
      console.log('⚠️  Content field missing');
    }
    
    if (notificationData.id) {
      console.log(`✅ ID field exists: ${notificationData.id}`);
    }
    
    if (notificationData.scheduledTime) {
      console.log(`✅ Scheduled time exists: ${notificationData.scheduledTime}`);
    }
    
    console.log('\n✅ Test completed successfully!');
    
  } catch (error) {
    console.error('\n❌ Test failed with error:');
    console.error('Error message:', error.message);
    console.error('Error type:', error.name);
    
    if (error.stack) {
      console.error('\nStack trace:');
      console.error(error.stack);
    }
    
    process.exit(1);
  }
}

// Run the test
testGetNotificationContent();
