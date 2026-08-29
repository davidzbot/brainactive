$signature = @'
[DllImport("advapi32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
public static extern bool CredRead(string target, uint type, int reservedFlag, out IntPtr credentialPtr);
[DllImport("advapi32.dll", SetLastError = true)]
public static extern void CredFree(IntPtr cred);
'@
Add-Type -MemberDefinition $signature -Namespace Win32 -Name Cred

foreach ($t in @(1, 4)) {
  $ptr = [IntPtr]::Zero
  $ok = [Win32.Cred]::CredRead("Supabase CLI:supabase", $t, 0, [ref]$ptr)
  Write-Host ("=== type=$t ok=$ok ptr=$ptr ===")
  if (-not $ok) { continue }
  # dump first 120 bytes as hex + ascii
  $raw = New-Object byte[] 120
  [System.Runtime.InteropServices.Marshal]::Copy($ptr, $raw, 0, 120)
  $hex = ($raw | ForEach-Object { $_.ToString("x2") }) -join " "
  Write-Host ("raw hex: " + $hex.Substring(0, [Math]::Min(240, $hex.Length)))
  # try reading string fields at various offsets
  foreach ($off in @(8,16,24,56,64,72)) {
    $p = [System.Runtime.InteropServices.Marshal]::ReadIntPtr($ptr, $off)
    if ($p -ne [IntPtr]::Zero) {
      $s = [System.Runtime.InteropServices.Marshal]::PtrToStringUni($p)
      Write-Host ("  off $off str: " + $s.Substring(0, [Math]::Min(40, $s.Length)))
    }
  }
  # blob size + ptr
  $sz = [System.Runtime.InteropServices.Marshal]::ReadInt32($ptr, 32)
  $bp = [System.Runtime.InteropServices.Marshal]::ReadIntPtr($ptr, 40)
  Write-Host ("  size@32=$sz  blobptr@40=$bp")
  if ($bp -ne [IntPtr]::Zero -and $sz -gt 0 -and $sz -lt 4000) {
    $bb = New-Object byte[] $sz
    [System.Runtime.InteropServices.Marshal]::Copy($bp, $bb, 0, $sz)
    Write-Host ("  blob utf8: " + [System.Text.Encoding]::UTF8.GetString($bb).Substring(0, [Math]::Min(40, $sz)))
  }
  [Win32.Cred]::CredFree($ptr)
}
