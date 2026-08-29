"""
QA Suite for Phases 5, 6, and 7 of BrainActive Build
"""

import os
import re
import subprocess

def test_backend_isolation():
    print("=== [QA Phase 7.1] Backend Isolation Verification ===")
    search_dirs = [
        "C:/Projects/brainactive-android/src",
        "C:/Projects/brainactive-android/supabase/functions",
        "C:/Projects/brainactive-android/supabase/migrations"
    ]
    
    forbidden_patterns = [
        r'\bmath_questions\b',
        r'\bmath_attempts\b',
        r'\bmath_progress\b',
        r'\bmath_profiles\b',
        r'\bmath-app-',
        r'\bmath-get-',
        r'\bmath-submit-',
        r'\bpsle_questions\b',
        r'\bpsle_attempts\b',
        r'\bpsle-app-'
    ]
    
    violations = []
    for sdir in search_dirs:
        for root, dirs, files in os.walk(sdir):
            for f in files:
                if f.endswith(('.ts', '.tsx', '.js', '.jsx', '.sql', '.toml')):
                    fpath = os.path.join(root, f)
                    with open(fpath, 'r', encoding='utf-8', errors='ignore') as fo:
                        content = fo.read()
                        for pat in forbidden_patterns:
                            if re.search(pat, content):
                                violations.append((fpath, pat))
                                
    if violations:
        print(f"FAILED: Found forbidden production references: {violations}")
        assert False, "Backend isolation check failed!"
    else:
        print("[OK] Complete Backend Isolation Verified: 0 references to MathHero/PSLE production resources.")
    print("[PASS] Backend Isolation Verified\n")

def test_frontend_routes_and_pages():
    print("=== [QA Phase 7.2] Frontend Pages & Routes Verification ===")
    
    expected_pages = [
        "C:/Projects/brainactive-android/src/pages/home/index.tsx",
        "C:/Projects/brainactive-android/src/pages/quiz/index.tsx",
        "C:/Projects/brainactive-android/src/pages/quiz/QuizContent.tsx",
        "C:/Projects/brainactive-android/src/pages/result/index.tsx",
        "C:/Projects/brainactive-android/src/pages/result/ResultContent.tsx",
        "C:/Projects/brainactive-android/src/pages/pro/index.tsx"
    ]
    
    for p in expected_pages:
        assert os.path.exists(p), f"Page file {p} missing!"
        print(f"[OK] Page exists: {os.path.basename(os.path.dirname(p))}/{os.path.basename(p)}")
        
    # Check app.config.ts
    cfg_path = "C:/Projects/brainactive-android/src/app.config.ts"
    with open(cfg_path, 'r', encoding='utf-8') as f:
        cfg = f.read()
        assert "pages/home/index" in cfg
        assert "pages/quiz/index" in cfg
        assert "pages/result/index" in cfg
        assert "pages/pro/index" in cfg
    print("[OK] All pages registered in app.config.ts")
    print("[PASS] Frontend Pages & Routing Verified\n")

def test_variance_report():
    print("=== [QA Phase 7.3] Variance Report Verification ===")
    report_path = "C:/Projects/brainactive-android/revamp/report/mathhero_brainactive_variance.md"
    assert os.path.exists(report_path), "Variance report missing!"
    
    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()
        required_sections = [
            "Home Page", "Quick Test", "Daily Limits", "Question Page",
            "Pro", "Referral", "AdMob", "Database & Backend Isolation Verification"
        ]
        for s in required_sections:
            assert s in content, f"Section '{s}' missing in variance report!"
            print(f"[OK] Section '{s}' documented in variance report")
            
    print("[PASS] Variance Report Verified\n")

if __name__ == '__main__':
    test_backend_isolation()
    test_frontend_routes_and_pages()
    test_variance_report()
    print("==============================================")
    print("ALL QA CHECKS FOR PHASES 5, 6, AND 7 PASSED!")
    print("==============================================")
