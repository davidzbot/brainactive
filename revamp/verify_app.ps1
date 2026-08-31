$anon='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1xcHVuanZkcmtxdmlvbnNqb3NsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY0NTk5MTYsImV4cCI6MjA5MjAzNTkxNn0.65Yda6PICedefQLGex5OuS1IOFNeJaHgBuG3mGfoI3s'
$r=Invoke-RestMethod -Uri 'https://mqpunjvdrkqvionsjosl.supabase.co/functions/v1/brainactive-get-questions?mode=quick_test&limit=1000' -Headers @{apikey=$anon; Authorization="Bearer $anon"}
Write-Host ("returned "+ $r.data.Count)
Write-Host ("first "+ $r.data[0].id)
$r2=Invoke-RestMethod -Uri 'https://mqpunjvdrkqvionsjosl.supabase.co/functions/v1/brainactive-get-questions?mode=pro_practice&limit=1000' -Headers @{apikey=$anon; Authorization="Bearer $anon"}
Write-Host ("pro returned "+ $r2.data.Count)
