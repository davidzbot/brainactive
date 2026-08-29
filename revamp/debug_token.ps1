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

$u8 = [System.Text.Encoding]::UTF8.GetString($blob)
$uni = [System.Text.Encoding]::Unicode.GetString($blob)
Write-Host ("size=$size  utf8len=$($u8.Length)  unilen=$($uni.Length)")
Write-Host ("utf8: [" + $u8.Substring(0, [Math]::Min(30, $u8.Length)) + "]")
Write-Host ("uni : [" + $uni.Substring(0, [Math]::Min(30, $uni.Length)) + "]")

foreach ($tok in @($u8, $uni)) {
  try {
    $r = Invoke-RestMethod -Uri "https://api.supabase.com/v1/projects/mqpunjvdrkqvionsjosl/api-keys" -Headers @{"Authorization"="Bearer $tok"} -ErrorAction Stop
    Write-Host ("  api-keys OK with token len $($tok.Length): " + $r.Count + " keys")
  } catch {
    Write-Host ("  api-keys 401 with token len $($tok.Length)")
  }
}
