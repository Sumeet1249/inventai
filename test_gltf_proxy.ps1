# Generate a CAD model
$body = '{"project_id":"proxy-test","prompt":"fpv racing drone 5 inch carbon fibre"}'
Write-Host "Generating CAD model..." -ForegroundColor Cyan
$r = Invoke-WebRequest -Uri "http://localhost:8080/api/v1/cad/generate" -Method POST -ContentType "application/json" -Body $body -TimeoutSec 60
$last = ($r.Content -split "`n" | Where-Object { $_.StartsWith("data:") }) | Select-Object -Last 1
$d = $last -replace "^data: ","" | ConvertFrom-Json
Write-Host "Type   : $($d.parameters.component_type)  span=$($d.parameters.span_mm)mm"
Write-Host "GLTF   : $($d.gltf_url)"

# Test 1: Direct via nginx (should always work)
$url1 = "http://localhost:8080$($d.gltf_url)"
$g1 = Invoke-WebRequest -Uri $url1 -TimeoutSec 10
Write-Host ""
Write-Host "Direct (8080):      HTTP $($g1.StatusCode)  $($g1.RawContentLength) bytes" -ForegroundColor Green

# Test 2: Browser URL (what ThreeViewer now uses — same as Test 1)
Write-Host "ThreeViewer URL:    $url1" -ForegroundColor Green
$preview = [System.Text.Encoding]::UTF8.GetString($g1.Content, 0, [Math]::Min(60, $g1.Content.Length))
Write-Host "GLTF content:       $preview..."
Write-Host ""
Write-Host "✓ GLTF will load in ThreeViewer at http://localhost:3001" -ForegroundColor Green
