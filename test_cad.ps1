param([string]$Prompt = "Design a foldable hexacopter frame 550mm span for heavy lift photography")

$body = "{`"project_id`":`"test`",`"prompt`":`"$Prompt`"}"
Write-Host "`nTesting: $Prompt" -ForegroundColor Cyan
Write-Host "─────────────────────────────────────────"

$r     = Invoke-WebRequest -Uri "http://localhost:8080/api/v1/cad/generate" `
             -Method POST -ContentType "application/json" -Body $body -TimeoutSec 90
$lines = $r.Content -split "`n" | Where-Object { $_.StartsWith("data:") }

Write-Host "SSE events received: $($lines.Count)" -ForegroundColor Yellow

foreach ($line in $lines) {
    $d = $line -replace "^data: ","" | ConvertFrom-Json -ErrorAction SilentlyContinue
    if ($null -eq $d) { continue }
    $stage = if ($d.stage) { "[Stage $($d.stage)]" } else { "[Final]  " }
    Write-Host "$stage $($d.status)" -ForegroundColor $(if ($d.gltf_url) {"Green"} else {"Gray"})
}

# Final event
$last = ($lines | Select-Object -Last 1) -replace "^data: ","" | ConvertFrom-Json
Write-Host ""
Write-Host "Component : $($last.parameters.component_type)" -ForegroundColor Green
Write-Host "Span      : $($last.parameters.span_mm) mm"
Write-Host "Arms      : $($last.parameters.arm_count)"
Write-Host "Wall      : $($last.parameters.wall_mm) mm"
Write-Host "GLTF URL  : $($last.gltf_url)"
if ($last.warnings)            { Write-Host "Warnings  : $($last.warnings -join ', ')" -ForegroundColor Yellow }
if ($last.validation_warnings) { Write-Host "Validation: $($last.validation_warnings -join ', ')" -ForegroundColor Yellow }

# Verify GLTF file
if ($last.gltf_url) {
    $g = Invoke-WebRequest -Uri "http://localhost:8080$($last.gltf_url)" -TimeoutSec 10
    $preview = [System.Text.Encoding]::UTF8.GetString($g.Content, 0, [Math]::Min(60,$g.Content.Length))
    Write-Host "GLTF size : $($g.RawContentLength) bytes  [$preview...]" -ForegroundColor Green
}
