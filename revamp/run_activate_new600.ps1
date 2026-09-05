$proj = "mqpunjvdrkqvionsjosl"
$sig = @'
[DllImport("advapi32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
public static extern bool CredRead(string target, uint type, int reservedFlag, out IntPtr credentialPtr);
[DllImport("advapi32.dll", SetLastError = true)]
public static extern void CredFree(IntPtr cred);
'@
Add-Type -MemberDefinition $sig -Namespace Win32 -Name Cred
$ptr = [IntPtr]::Zero
[Win32.Cred]::CredRead("Supabase CLI:supabase", 1, 0, [ref]$ptr) | Out-Null
$blob = [byte[]]::new([System.Runtime.InteropServices.Marshal]::ReadInt32($ptr, 32))
[System.Runtime.InteropServices.Marshal]::Copy([System.Runtime.InteropServices.Marshal]::ReadIntPtr($ptr, 40), $blob, 0, $blob.Length)
[Win32.Cred]::CredFree($ptr)
$tok = [System.Text.Encoding]::UTF8.GetString($blob)
$keys = Invoke-RestMethod -Uri "https://api.supabase.com/v1/projects/$proj/api-keys" -Headers @{"Authorization"="Bearer $tok"}
$sr = ($keys | Where-Object { $_.name -eq 'service_role' }).api_key
$env:BA_SR = $sr
& "C:\Users\zhang\AppData\Local\Programs\Python\Python310\python.exe" "C:\Projects\brainactive-android\revamp\bank\new_600\activate_new600.py" @args
