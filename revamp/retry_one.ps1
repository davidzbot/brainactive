$sig = @'
[DllImport("advapi32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
public static extern bool CredRead(string target, uint type, int reservedFlag, out IntPtr credentialPtr);
[DllImport("advapi32.dll", SetLastError = true)]
public static extern void CredFree(IntPtr cred);
'@
Add-Type -MemberDefinition $sig -Namespace Win32 -Name Cred
$ptr = [IntPtr]::Zero
[Win32.Cred]::CredRead("Supabase CLI:supabase", 1, 0, [ref]$ptr) | Out-Null
$size = [System.Runtime.InteropServices.Marshal]::ReadInt32($ptr, 32)
$bp = [System.Runtime.InteropServices.Marshal]::ReadIntPtr($ptr, 40)
$blob = [byte[]]::new($size)
[System.Runtime.InteropServices.Marshal]::Copy($bp, $blob, 0, $size)
[Win32.Cred]::CredFree($ptr)
$tok = [System.Text.Encoding]::UTF8.GetString($blob)
$keys = Invoke-RestMethod -Uri "https://api.supabase.com/v1/projects/mqpunjvdrkqvionsjosl/api-keys" -Headers @{"Authorization"="Bearer $tok"}
$sr = ($keys | Where-Object { $_.name -eq 'service_role' }).api_key
$bytes = [System.IO.File]::ReadAllBytes("C:\Projects\brainactive-android\revamp\bank\images\BA_P3_1027.svg")
$url = "https://mqpunjvdrkqvionsjosl.supabase.co/storage/v1/object/brainactive-assets/p3/BA_P3_1027.svg"
$sh = @{"Authorization"="Bearer $sr"; "apikey"=$sr; "Content-Type"="image/svg+xml"; "x-upsert"="true"}
try { Invoke-RestMethod -Uri $url -Method Post -Headers $sh -Body $bytes -ErrorAction Stop; Write-Host "RETRY OK" } catch { Write-Host ("RETRY FAIL: " + $_.Exception.Message) }
