$sig = @"
[DllImport("advapi32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
public static extern bool CredRead(string target, uint type, int reservedFlag, out IntPtr credentialPtr);
[DllImport("advapi32.dll", SetLastError = true)]
public static extern void CredFree(IntPtr cred);
"@
Add-Type -MemberDefinition $sig -Namespace Win32 -Name CredBA
$ptr = [IntPtr]::Zero
[Win32.CredBA]::CredRead("Supabase CLI:supabase", 1, 0, [ref]$ptr) | Out-Null
$blob = [byte[]]::new([System.Runtime.InteropServices.Marshal]::ReadInt32($ptr, 32))
[System.Runtime.InteropServices.Marshal]::Copy([System.Runtime.InteropServices.Marshal]::ReadIntPtr($ptr, 40), $blob, 0, $blob.Length)
[Win32.CredBA]::CredFree($ptr)
$env:BA_PAT = [System.Text.Encoding]::UTF8.GetString($blob)
$keys = Invoke-RestMethod -Uri "https://api.supabase.com/v1/projects/mqpunjvdrkqvionsjosl/api-keys" -Headers @{"Authorization"="Bearer $($env:BA_PAT)"}
$env:BA_SR = ($keys | Where-Object { $_.name -eq "service_role" }).api_key
$env:PYTHONIOENCODING = "utf-8"
Write-Host "env ready"

