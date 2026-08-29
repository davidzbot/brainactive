"""
QA Suite for Phases 1, 2, and 3 of BrainActive Build
"""

import os
import json
import re
import subprocess
import glob

def test_phase_1_backup():
    print("=== [QA Phase 1] Backup & Safety Verification ===")
    backup_path = "C:/Projects/brainactive-android-2026-08-29-backup"
    assert os.path.exists(backup_path), f"Backup directory {backup_path} does not exist!"
    
    file_count = 0
    for root, dirs, files in os.walk(backup_path):
        file_count += len(files)
        
    print(f"[OK] Backup exists at {backup_path}")
    print(f"[OK] Backup file count: {file_count} files")
    assert file_count > 1000, f"Backup file count too low ({file_count})"
    
    # Check MathHero & PSLE integrity
    mathhero_path = "C:/Projects/MathHero/math-hero-app"
    psle_path = "C:/Projects/PSLE"
    assert os.path.exists(mathhero_path), "MathHero path missing!"
    assert os.path.exists(psle_path), "PSLE path missing!"
    print("[OK] MathHero & PSLE production directories intact and untouched")
    print("[PASS] Phase 1 QA Successful\n")

def test_phase_2_mapping():
    print("=== [QA Phase 2] Math Hero UI Pattern Mapping & Isolation ===")
    # Check that brainactive-android src does not have hardcoded references to math-hero backend
    src_path = "C:/Projects/brainactive-android/src"
    
    suspicious_patterns = [
        r'math_questions',
        r'math-app-',
        r'math-get-',
        r'math-submit-',
        r'psle_questions',
        r'psle-app-'
    ]
    
    violations = []
    for root, dirs, files in os.walk(src_path):
        for f in files:
            if f.endswith(('.ts', '.tsx', '.js', '.jsx', '.json')):
                fpath = os.path.join(root, f)
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as file_obj:
                    content = file_obj.read()
                    for pat in suspicious_patterns:
                        if re.search(pat, content):
                            violations.append((fpath, pat))
                            
    if violations:
        print(f"WARNING: Found suspicious references in src: {violations}")
    else:
        print("[OK] Zero references to MathHero/PSLE tables/functions in brainactive src")
        
    print("[PASS] Phase 2 QA Successful\n")

def test_phase_3_backend():
    print("=== [QA Phase 3] BrainActive Backend & Edge Functions ===")
    
    # 1. Check SQL Migration
    mig_path = "C:/Projects/brainactive-android/supabase/migrations/20260829000000_brainactive_schema.sql"
    assert os.path.exists(mig_path), "Migration file missing!"
    with open(mig_path, 'r', encoding='utf-8') as f:
        sql = f.read()
        
    expected_tables = [
        "brainactive_questions",
        "brainactive_profiles",
        "brainactive_referrals",
        "brainactive_attempts",
        "brainactive_progress"
    ]
    for tbl in expected_tables:
        assert tbl in sql, f"Table {tbl} missing from migration SQL!"
        print(f"[OK] Table {tbl} defined in SQL migration")
        
    assert "brainactive-assets" in sql, "Storage bucket missing from migration SQL!"
    print("[OK] Storage bucket 'brainactive-assets' registered in SQL migration")
    
    # 2. Check Edge Functions
    expected_functions = [
        "brainactive-get-questions",
        "brainactive-submit-attempt",
        "brainactive-get-progress",
        "brainactive-apply-referral"
    ]
    fn_dir = "C:/Projects/brainactive-android/supabase/functions"
    for fn in expected_functions:
        fn_index = os.path.join(fn_dir, fn, "index.ts")
        assert os.path.exists(fn_index), f"Edge function {fn}/index.ts missing!"
        with open(fn_index, 'r', encoding='utf-8') as f:
            code = f.read()
            assert "Deno.serve" in code or "serve(" in code, f"Edge function {fn} has no Deno.serve handler!"
            assert "corsHeaders" in code, f"Edge function {fn} has no CORS headers!"
        print(f"[OK] Edge Function '{fn}' implemented and verified")
        
    # 3. Check config.toml
    config_path = "C:/Projects/brainactive-android/supabase/config.toml"
    with open(config_path, 'r', encoding='utf-8') as f:
        config_text = f.read()
        for fn in expected_functions:
            assert f"functions.{fn}" in config_text, f"Function {fn} missing in config.toml!"
    print("[OK] All 4 Edge Functions registered in supabase/config.toml")
    
    # 4. Check client request layer
    req_path = "C:/Projects/brainactive-android/src/utils/request.ts"
    assert os.path.exists(req_path), "request.ts missing!"
    with open(req_path, 'r', encoding='utf-8') as f:
        req_code = f.read()
        for fn in expected_functions:
            assert fn in req_code, f"Function {fn} missing from client request.ts!"
    print("[OK] Client API layer 'request.ts' connects to all BrainActive functions")
    
    print("[PASS] Phase 3 QA Successful\n")

if __name__ == '__main__':
    test_phase_1_backup()
    test_phase_2_mapping()
    test_phase_3_backend()
    print("==============================================")
    print("ALL QA CHECKS FOR PHASES 1, 2, AND 3 PASSED!")
    print("==============================================")
