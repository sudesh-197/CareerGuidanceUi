"""
Quick test script to verify backend modules are working
"""



print("Testing backend modules...")
print("-" * 50)

# Test 1: Import modules
try:
    from app.services.analysis.resume_analyzer import ResumeAnalyzer
    print("✓ ResumeAnalyzer imported successfully")
except Exception as e:
    print(f"✗ ResumeAnalyzer import failed: {e}")

try:
    from app.services.analysis.skill_engine import SkillEngine
    print("✓ SkillEngine imported successfully")
except Exception as e:
    print(f"✗ SkillEngine import failed: {e}")

try:
    from app.services.analysis.report_generator import ReportGenerator
    print("✓ ReportGenerator imported successfully")
except Exception as e:
    print(f"✗ ReportGenerator import failed: {e}")

print("-" * 50)

# Test 2: Initialize classes
try:
    analyzer = ResumeAnalyzer()
    print("✓ ResumeAnalyzer initialized")
except Exception as e:
    print(f"✗ ResumeAnalyzer initialization failed: {e}")

try:
    engine = SkillEngine()
    print("✓ SkillEngine initialized")
except Exception as e:
    print(f"✗ SkillEngine initialization failed: {e}")

try:
    generator = ReportGenerator()
    print("✓ ReportGenerator initialized")
except Exception as e:
    print(f"✗ ReportGenerator initialization failed: {e}")

print("-" * 50)

# Test 3: Test basic functionality
try:
    engine = SkillEngine()
    test_skills = {'python', 'javascript', 'react', 'sql'}
    result = engine.calculate_readiness_score(
        test_skills,
        'Software Development',
        3,
        True,
        True
    )
    print(f"✓ Readiness score calculation works: {result['total_score']}%")
except Exception as e:
    print(f"✗ Readiness score calculation failed: {e}")

print("-" * 50)
print("Backend test complete!")
