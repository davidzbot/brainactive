$mqUrl = 'https://mqpunjvdrkqvionsjosl.supabase.co'
$anon  = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1xcHVuanZkcmtxdmlvbnNqb3NsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY0NTk5MTYsImV4cCI6MjA5MjAzNTkxNn0.QLjWtVdGvFgTajL5Q51MoAbLyV46inSFsIGtAJBDXbE'
$h = @{'apikey'=$anon; 'Authorization'="Bearer $anon"; 'Content-Type'='application/json'; 'x-device-id'='reverify_device'}
$results = [System.Collections.ArrayList]@()
function chk($n,$c){ $r = if($c){'PASS'}else{'FAIL'}; [void]$results.Add("$n : $r"); Write-Host ("  [$n] $r") }
function J($u,$m='GET',$b=$null){ try { if($b){ Invoke-RestMethod -Uri $u -Method $m -Headers $h -Body ($b|ConvertTo-Json -Depth 10) -UseBasicParsing } else { Invoke-RestMethod -Uri $u -Method $m -Headers $h -UseBasicParsing } } catch { return $null } }

Write-Host "`n== Flow 3: Quick Test retrieval (exactly 5) =="
$q = J "$mqUrl/functions/v1/brainactive-get-questions?mode=quick_test&limit=5"
chk 'get-questions-returns-5' ($q -and $q.success -and $q.data.Count -eq 5)

Write-Host "`n== Flow 4/5: Topic+Level + image loads =="
$tlMissing=0; foreach($d in $q.data){ if(-not ($d.topic -and $d.level)){ $tlMissing++ } }
chk 'topic+level-present' ($tlMissing -eq 0)
$imgOk=0;$imgFail=0
foreach($d in $q.data){ if($d.image_path){ $iu="$mqUrl/storage/v1/object/public/brainactive-assets/$($d.image_path)"; try{ $r=Invoke-WebRequest -Uri $iu -UseBasicParsing -Method Get -ErrorAction Stop; if($r.StatusCode -eq 200){$imgOk++}else{$imgFail++} }catch{$imgFail++} } }
chk 'images-load-5of5' ($imgOk -eq 5 -and $imgFail -eq 0)

Write-Host "`n== Flow 6/7/8: submit + progress =="
$att=@(); for($i=0;$i-lt$q.data.Count;$i++){ $qq=$q.data[$i]; $sel=if($i-lt3){$qq.answer}else{($qq.options|Where-Object{$_.id-ne$qq.answer}|Select-Object -First 1).id}; $att+=@{question_id=$qq.id;selected_answer=$sel;is_correct=($sel-eq$qq.answer);time_spent_ms=1000;topic=$qq.topic;level=$qq.level} }
$sub=J "$mqUrl/functions/v1/brainactive-submit-attempt" -m POST -b @{user_id='reverify_user_A';attempts=$att;session_id='rv1';mode='quick_test'}
chk 'submit-attempt' ($sub -and $sub.success -and $sub.data.session_total -eq 5)
$p=J "$mqUrl/functions/v1/brainactive-get-progress?user_id=reverify_user_A"
chk 'progress-streak-daily' ($p -and $p.success -and $p.data.streak_count -ge 1 -and $p.data.daily_rounds_completed -ge 1)

Write-Host "`n== Flow 13: referral =="
$ref=J "$mqUrl/functions/v1/brainactive-get-progress?user_id=reverify_referrer_B"
$code=$ref.data.referral_code
$apply=J "$mqUrl/functions/v1/brainactive-apply-referral" -m POST -b @{user_id='reverify_referee_C';referral_code=$code}
$pC=J "$mqUrl/functions/v1/brainactive-get-progress?user_id=reverify_referee_C"
chk 'referral-grants-pro' ($apply -and $apply.success -and $pC.data.is_pro -eq $true)
$invBody=$null; try { Invoke-RestMethod -Uri "$mqUrl/functions/v1/brainactive-apply-referral" -Method Post -Headers $h -Body '{"user_id":"reverify_X","referral_code":"ZZZZZZ"}' -UseBasicParsing -ErrorAction Stop } catch { $rs=$_.Exception.Response; $invBody=(New-Object System.IO.StreamReader($rs.GetResponseStream())).ReadToEnd() | ConvertFrom-Json }
chk 'referral-invalid-rejected' ($invBody -and $invBody.error.code -eq 'INVALID_CODE')

Write-Host "`n== get-content contract (app expects {success,data}) =="
$c1=J "$mqUrl/functions/v1/brainactive-get-content?lang=en&type=name&limit=20"
$ok1 = $c1 -and $c1.success -and ($c1.data -is [array]) -and $c1.data.Count -gt 0 -and $c1.data.Count -le 20
foreach($row in $c1.data){ if($row.type -ne 'name' -or $row.language -ne 'en'){ $ok1=$false } }
chk 'content-en-name-limit' $ok1
$c2=J "$mqUrl/functions/v1/brainactive-get-content?lang=zh&type=sentence&limit=5"
$ok2 = $c2 -and $c2.success -and ($c2.data -is [array]) -and $c2.data.Count -gt 0 -and $c2.data.Count -le 5
foreach($row in $c2.data){ if($row.type -ne 'sentence' -or $row.language -ne 'zh'){ $ok2=$false } }
chk 'content-zh-sentence-limit5' $ok2

Write-Host "`n== SUMMARY =="
foreach($line in $results){ Write-Host ("  $line") }
$fails=($results | Where-Object { $_ -like '*FAIL' } | Measure-Object).Count
Write-Host ("  TOTAL FAILS: $fails")
