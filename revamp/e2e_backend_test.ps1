$mqUrl = 'https://mqpunjvdrkqvionsjosl.supabase.co'
$anon  = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1xcHVuanZkcmtxdmlvbnNqb3NsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY0NTk5MTYsImV4cCI6MjA5MjAzNTkxNn0.QLjWtVdGvFgTajL5Q51MoAbLyV46inSFsIGtAJBDXbE'
$h = @{'apikey'=$anon; 'Authorization'="Bearer $anon"; 'Content-Type'='application/json'; 'x-device-id'='test_e2e_device'}

function J($u,$m='GET',$b=$null){ try { if($b){ Invoke-RestMethod -Uri $u -Method $m -Headers $h -Body ($b|ConvertTo-Json -Depth 10) -UseBasicParsing } else { Invoke-RestMethod -Uri $u -Method $m -Headers $h -UseBasicParsing } } catch { $e=$_.Exception; return @{ok=$false; status=$e.Response.StatusCode.value__; body=$e.Message} } }
function Show($o){ if($o -is [hashtable]){ "    ok=$($o.ok) status=$($o.status) msg=$($o.body)" } else { $o | ConvertTo-Json -Depth 6 -Compress } }

Write-Host "`n===== 3. Quick Test retrieval (exactly 5) ====="
$q = J "$mqUrl/functions/v1/brainactive-get-questions?mode=quick_test&limit=5"
if($q.success){ $data=$q.data; Write-Host ("  RETURNED " + $data.Count + " questions"); $ok = $data.Count -eq 5; Write-Host ("  exactly 5? " + $ok); foreach($d in $data){ Write-Host ("    id=$($d.id) topic=$($d.topic) level=$($d.level) img=$($d.image_path) is_active=$($d.is_active)") } } else { Write-Host "  FAIL"; Show $q }

Write-Host "`n===== 4/5. Topic+Level present, image URL loads (public) ====="
$imgOk=0; $imgFail=0
foreach($d in $data){
  $hasTL = ($d.topic -and $d.level)
  Write-Host ("  topic+level present: $hasTL (topic=$($d.topic), level=$($d.level))")
  if($d.image_path){
    $iu = "$mqUrl/storage/v1/object/public/brainactive-assets/$($d.image_path)"
    try { $r=Invoke-WebRequest -Uri $iu -UseBasicParsing -Method Get -ErrorAction Stop; if($r.StatusCode -eq 200){$imgOk++} else {$imgFail++} } catch { $imgFail++ }
  }
}
Write-Host ("  images loaded OK=$imgOk fail=$imgFail")

Write-Host "`n===== 6/7. Answer selection + submit attempt ====="
$attempts=@(); $corr=0
for($i=0;$i -lt $data.Count;$i++){
  $qq=$data[$i]; $sel = if($i -lt 3){ $qq.answer } else { ($qq.options | Where-Object { $_.id -ne $qq.answer } | Select-Object -First 1).id }
  $isc = ($sel -eq $qq.answer); if($isc){$corr++}
  $attempts += @{ question_id=$qq.id; selected_answer=$sel; is_correct=$isc; time_spent_ms=1000; topic=$qq.topic; level=$qq.level }
}
$sub = J "$mqUrl/functions/v1/brainactive-submit-attempt" -m POST -b @{ user_id='test_e2e_user_A'; attempts=$attempts; session_id='sess_e2e_1'; mode='quick_test' }
if($sub.success){ Write-Host ("  submit OK: " + ($sub.data | ConvertTo-Json -Compress)) } else { Write-Host "  FAIL"; Show $sub }

Write-Host "`n===== 8/9/10/11. Progress + streak + daily + pro ====="
$p = J "$mqUrl/functions/v1/brainactive-get-progress?user_id=test_e2e_user_A"
if($p.success){ Write-Host ("  progress: " + ($p.data | ConvertTo-Json -Compress)) } else { Write-Host "  FAIL"; Show $p }

Write-Host "`n===== 13. Referral flow ====="
# create referrer profile (auto code) then apply
$ref = J "$mqUrl/functions/v1/brainactive-get-progress?user_id=test_e2e_referrer_B"
$code = $ref.data.referral_code
Write-Host ("  referrer code = $code")
$apply = J "$mqUrl/functions/v1/brainactive-apply-referral" -m POST -b @{ user_id='test_e2e_referee_C'; referral_code=$code }
if($apply.success){ Write-Host ("  apply OK: " + ($apply.data | ConvertTo-Json -Compress)) } else { Write-Host "  FAIL"; Show $apply }
$pC = J "$mqUrl/functions/v1/brainactive-get-progress?user_id=test_e2e_referee_C"
Write-Host ("  referee is_pro after apply = " + $pC.data.is_pro)

Write-Host "`n===== 12. Content (get-content) ====="
$c = J "$mqUrl/functions/v1/brainactive-get-content?lang=en&limit=20"
Write-Host ("  raw body keys: " + (($c | Get-Member -MemberType NoteProperty).Name -join ','))
Write-Host ("  returned data is array? " + ($c.data -is [array]) + " count=" + $(if($c.data -is [array]){$c.data.Count}else{'n/a'}))

Write-Host "`n===== 14. Error / fallback behaviour ====="
$inv = J "$mqUrl/functions/v1/brainactive-apply-referral" -m POST -b @{ user_id='test_e2e_X'; referral_code='ZZZZZZ' }
Write-Host ("  invalid referral code -> success=$($inv.success) code=$($inv.error.code)")
$retry = J "$mqUrl/functions/v1/brainactive-get-questions?mode=retry&ids=BA_NOSUCH"
if($retry.success){ Write-Host ("  retry unknown ids -> returned " + $retry.data.Count + " (empty expected)") } else { Write-Host "  FAIL"; Show $retry }

Write-Host "`n===== DONE (questions still active; deactivation is a separate step) ====="
