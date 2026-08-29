$signature = @'
[DllImport("advapi32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
public static extern bool CredRead(string target, uint type, int reservedFlag, out IntPtr credentialPtr);
[DllImport("advapi32.dll", SetLastError = true)]
public static extern void CredFree(IntPtr cred);
'@
Add-Type -MemberDefinition $signature -Namespace Win32 -Name Cred

$ptr = [IntPtr]::Zero
[Win32.Cred]::CredRead("Supabase CLI:supabase", 1, 0, [ref]$ptr) | Out-Null
$size = [System.Runtime.InteropServices.Marshal]::ReadInt32($ptr, 32)
$blobPtr = [System.Runtime.InteropServices.Marshal]::ReadIntPtr($ptr, 40)
$blob = [byte[]]::new($size)
[System.Runtime.InteropServices.Marshal]::Copy($blobPtr, $blob, 0, $size)
[Win32.Cred]::CredFree($ptr)
$token = [System.Text.Encoding]::UTF8.GetString($blob)
Write-Host ("token prefix: " + $token.Substring(0, [Math]::Min(12, $token.Length)) + " len " + $token.Length)

$keys = Invoke-RestMethod -Uri "https://api.supabase.com/v1/projects/mqpunjvdrkqvionsjosl/api-keys" -Headers @{"Authorization"="Bearer $token"}
$sr = ($keys | Where-Object { $_.name -eq 'service_role' }).api_key
Write-Host ("service_role prefix: " + $sr.Substring(0, 12))

$list = Get-Content "C:\Projects\brainactive-android\revamp\bank\upload_list.json" | ConvertFrom-Json
$proj = "mqpunjvdrkqvionsjosl"
$okc = 0; $fail = 0; $fails = @()
foreach ($item in $list) {
  $bytes = [System.IO.File]::ReadAllBytes($item.local)
  $ctype = if ($item.local -like "*.svg") { "image/svg+xml" } else { "image/png" }
  $url = "https://$proj.supabase.co/storage/v1/object/brainactive-assets/$($item.dest)"
  $sh = @{"Authorization"="Bearer $sr"; "apikey"=$sr; "Content-Type"=$ctype; "x-upsert"="true"}
  try {
    Invoke-RestMethod -Uri $url -Method Post -Headers $sh -Body $bytes -ErrorAction Stop
    $okc++
    if ($okc % 25 -eq 0) { Write-Host "progress: $okc/$($list.Count)" }
  } catch {
    $fail++; $fails += ($item.dest + " : " + $_.Exception.Message)
  }
}
Write-Host ("UPLOAD DONE: $okc ok, $fail fail out of $($list.Count)")
foreach ($f in $fails | Select-Object -First 10) { Write-Host ("  FAIL " + $f) }
