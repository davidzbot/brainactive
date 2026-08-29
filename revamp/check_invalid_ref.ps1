$anon='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1xcHVuanZkcmtxdmlvbnNqb3NsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY0NTk5MTYsImV4cCI6MjA5MjAzNTkxNn0.QLjWtVdGvFgTajL5Q51MoAbLyV46inSFsIGtAJBDXbE'
$h=@{apikey=$anon;Authorization="Bearer $anon";'Content-Type'='application/json'}
$body = @{user_id='test_e2e_X'; referral_code='ZZZZZZ'} | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://mqpunjvdrkqvionsjosl.supabase.co/functions/v1/brainactive-apply-referral' -Method Post -Headers $h -Body $body -UseBasicParsing -ErrorAction Stop
  Write-Host '  unexpected 2xx'
} catch {
  $r=$_.Exception.Response
  $b=(New-Object System.IO.StreamReader($r.GetResponseStream())).ReadToEnd()
  Write-Host ("  STATUS=" + $r.StatusCode + " BODY=" + $b)
}
