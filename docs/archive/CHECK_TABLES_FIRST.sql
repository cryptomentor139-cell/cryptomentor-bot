-- Check if user_automatons table exists
-- Run this FIRST before migration 005

SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name = 'user_automatons';

-- If the query returns NO ROWS, you need to run migrations 001 and 002 first!
-- If it returns 'user_automatons', you can proceed with migration 005
