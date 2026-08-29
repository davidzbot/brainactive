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
$anon = ($keys | Where-Object { $_.name -eq 'anon' }).api_key

# list objects in folder
$listUrl = "https://mqpunjvdrkqvionsjosl.supabase.co/storage/v1/object/list/brainactive-assets?prefix=p3"
$items = Invoke-RestMethod -Uri $listUrl -Method Post -Headers @{"Authorization"="Bearer $anon"; "apikey"=$anon; "Content-Type"="application/json"} -Body '{"prefix":"p3","limit":1000}'
Write-Host ("OBJECT COUNT in p3: " + $items.Count)

# test public GET of one image
$getUrl = "https://mqpunjvdrkqvionsjosl.supabase.co/storage/v1/object/public/brainactive-assets/p3/BA_P3_1027.svg"
try { $r = Invoke-WebRequest -Uri $getUrl -Method Head -ErrorAction Stop; Write-Host ("PUBLIC GET status: " + $r.StatusCode) } catch { Write-Host ("PUBLIC GET FAIL: " + $_.Exception.Message) }
