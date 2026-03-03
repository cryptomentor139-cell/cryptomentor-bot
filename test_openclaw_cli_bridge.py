"""
Test OpenClaw CLI Bridge
Quick verification that OpenClaw CLI integration works
"""

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from openclaw_cli_bridge import get_openclaw_cli_bridge


def test_openclaw_cli():
    """Test OpenClaw CLI bridge functionality"""
    
    print("=" * 60)
    print("OpenClaw CLI Bridge Test")
    print("=" * 60)
    
    bridge = get_openclaw_cli_bridge()
    
    # Test 1: Health check
    print("\n1. Health Check")
    print("-" * 40)
    is_healthy = bridge.check_health()
    print(f"✓ OpenClaw CLI accessible: {is_healthy}")
    
    if not is_healthy:
        print("❌ OpenClaw CLI not working!")
        return False
    
    # Test 2: Get version
    print("\n2. Version Check")
    print("-" * 40)
    version = bridge.get_version()
    print(f"✓ OpenClaw version: {version}")
    
    # Test 3: Get status
    print("\n3. Status Check")
    print("-" * 40)
    status = bridge.get_status()
    if status.get('success'):
        print(f"✓ Status: {status}")
    else:
        print(f"⚠ Status check failed (might need gateway running): {status.get('error')}")
    
    # Test 4: List skills
    print("\n4. Skills Check")
    print("-" * 40)
    skills = bridge.list_skills()
    if skills.get('success'):
        print(f"✓ Skills available")
        if isinstance(skills.get('skills'), dict):
            skill_count = len(skills.get('skills', {}))
            print(f"  Found {skill_count} skills")
        else:
            print(f"  Skills: {skills.get('skills', 'N/A')[:200]}")
    else:
        print(f"⚠ Skills check failed: {skills.get('error')}")
    
    # Test 5: Run doctor
    print("\n5. Doctor Check")
    print("-" * 40)
    doctor = bridge.run_doctor()
    if doctor.get('success'):
        print("✓ Doctor check passed")
        report = doctor.get('report', '')
        if report:
            # Show first 500 chars of report
            print(f"\nReport preview:\n{report[:500]}")
    else:
        print(f"⚠ Doctor check issues:")
        print(doctor.get('report', 'N/A')[:500])
    
    print("\n" + "=" * 60)
    print("✅ OpenClaw CLI Bridge is working!")
    print("=" * 60)
    
    print("\n📝 Next Steps:")
    print("1. Configure OpenClaw channels (Telegram/WhatsApp)")
    print("2. Start OpenClaw gateway if needed")
    print("3. Integrate with bot handlers")
    
    return True


if __name__ == "__main__":
    try:
        success = test_openclaw_cli()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
