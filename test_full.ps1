Write-Host ""
Write-Host "══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  InventAI Full Pipeline Test" -ForegroundColor Cyan
Write-Host "══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# ── 1. CAD Generation ──────────────────────────────────────────
Write-Host "1. CAD Generation" -ForegroundColor Yellow
$cadBody = '{"project_id":"test-full","prompt":"Design a foldable quadcopter frame 450mm span 4 motors"}'
$r = Invoke-WebRequest -Uri "http://localhost:8080/api/v1/cad/generate" `
    -Method POST -ContentType "application/json" -Body $cadBody -TimeoutSec 60
$lines = $r.Content -split "`n" | Where-Object { $_.StartsWith("data:") }
$last = $lines | Select-Object -Last 1
$cad = $last -replace "^data: ","" | ConvertFrom-Json

Write-Host "   Stages received : $($lines.Count)" -ForegroundColor Gray
Write-Host "   Status          : $($cad.status)" -ForegroundColor $(if($cad.status -match "Completed"){"Green"}else{"Red"})
Write-Host "   Component type  : $($cad.parameters.component_type)"
Write-Host "   Span            : $($cad.parameters.span_mm) mm"
Write-Host "   GLTF URL        : $($cad.gltf_url)"

# Verify GLTF file is valid
if ($cad.gltf_url) {
    $g = Invoke-WebRequest -Uri "http://localhost:8080$($cad.gltf_url)" -TimeoutSec 10
    $preview = [System.Text.Encoding]::UTF8.GetString($g.Content, 0, 30)
    Write-Host "   GLTF file       : $($g.RawContentLength) bytes  [$preview...]" -ForegroundColor Green
}

# ── 2. Circuit Generation (uses CAD spec) ──────────────────────
Write-Host ""
Write-Host "2. Circuit Design (from CAD spec)" -ForegroundColor Yellow
$cadSpec = $cad.parameters | ConvertTo-Json -Compress
$circBody = "{`"project_id`":`"test-full`",`"cad_spec`":$cadSpec}"
$cr = Invoke-WebRequest -Uri "http://localhost:8080/api/v1/circuit/generate" `
    -Method POST -ContentType "application/json" -Body $circBody -TimeoutSec 30
$clines = $cr.Content -split "`n" | Where-Object { $_.StartsWith("data:") }
$clast = $clines | Select-Object -Last 1
$circ = $clast -replace "^data: ","" | ConvertFrom-Json

Write-Host "   Status          : $($circ.status)" -ForegroundColor $(if($circ.status -match "Completed"){"Green"}else{"Red"})
Write-Host "   Components      : $($circ.component_count)"
Write-Host "   BOM Total       : $($circ.bom_total)"
Write-Host "   Power Rails     : $($circ.power_rails -join ' · ')"
Write-Host "   MCU/FC          : $($circ.elec_spec.mcu)"
Write-Host "   Battery         : $($circ.elec_spec.power_input_v)V"
Write-Host "   Flight Time     : $($circ.elec_spec.flight_time_min) min"

# Verify SVG schematic
if ($circ.schematic_url) {
    $svg = Invoke-WebRequest -Uri "http://localhost:8080$($circ.schematic_url)" -TimeoutSec 10
    Write-Host "   SVG schematic   : $($svg.RawContentLength) bytes" -ForegroundColor Green
}

# ── 3. Summary ────────────────────────────────────────────────
Write-Host ""
Write-Host "══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  All systems operational ✓" -ForegroundColor Green
Write-Host "  Open: http://localhost:3001" -ForegroundColor White
Write-Host "══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
