$token = (supabase auth token 2>$null).Trim()
Write-Host ("token prefix: " + $token.Substring(0, [Math]::Min(15, $token.Length)) + " len " + $token.Length)
$h = @{"Authorization"="Bearer $token"; "Content-Type"="application/json"}
try {
  $keys = Invoke-RestMethod -Uri "https://api.supabase.com/v1/projects/mqpunjvdrkqvionsjosl/api-keys" -Headers $h -ErrorAction Stop
  Write-Host ("api-keys returned " + $keys.Count + " entries")
  $sr = ($keys | Where-Object { $_.name -eq 'service_role' }).api_key
  Write-Host ("service_role prefix: " + $sr.Substring(0, 12))
  $proj = "mqpunjvdrkqvionsjosl"
  $url = "https://$proj.supabase.co/storage/v1/object/brainactive-assets/p3/BA_P3_0001.svg"
  $bytes = [System.IO.File]::ReadAllBytes("C:\Projects\brainactive-android\revamp\bank\images\BA_P3_0001.svg")
  $sh = @{"Authorization"="Bearer $sr"; "apikey"=$sr; "Content-Type"="image/svg+xml"; "x-upsert"="true"}
  $r = Invoke-RestMethod -Uri $url -Method Post -Headers $sh -Body $bytes -ErrorAction Stop
  Write-Host ("upload result: " + ($r | ConvertTo-Json -Compress))
} catch {
  Write-Host ("ERROR: " + $_.Exception.Message)
}
