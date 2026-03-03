try:
    print("Starting import...")
    import test_property_offline_mode_access as t
    print('Module imported successfully')
    print('Has test functions:', any(x.startswith('test_') for x in dir(t)))
    attrs = [x for x in dir(t) if not x.startswith('_')]
    print(f'Total attributes: {len(attrs)}')
    print('All attributes:', attrs[:20])
    
    # Check if pytest.skip was called
    if hasattr(t, 'SUPABASE_URL'):
        print(f'SUPABASE_URL in module: {bool(t.SUPABASE_URL)}')
    if hasattr(t, 'SUPABASE_KEY'):
        print(f'SUPABASE_KEY in module: {bool(t.SUPABASE_KEY)}')
        
except Exception as e:
    print('Error:', e)
    import traceback
    traceback.print_exc()
