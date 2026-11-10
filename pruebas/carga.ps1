param([ValidateRange(1,200)][int]$Cantidad=30)
$base='http://localhost:8080'
$conteo=@{web1=0;web2=0;web3=0}
$fallos=0
$tiempos=0.0
for($i=1;$i -le $Cantidad;$i++) {
  $cronometro=[System.Diagnostics.Stopwatch]::StartNew()
  try {
    $resp=Invoke-RestMethod -Uri "$base/whoami?prueba=$i" -Method Get -TimeoutSec 8
    if ($conteo.ContainsKey([string]$resp.nodo)) { $conteo[[string]$resp.nodo]++ }
    else { $fallos++ }
  } catch { $fallos++ }
  $cronometro.Stop()
  $tiempos+=$cronometro.Elapsed.TotalMilliseconds
}
Write-Host '--- CampusSoporte: resultado de balanceo ---'
Write-Host "Solicitudes: $Cantidad | Exitosas: $($Cantidad-$fallos) | Fallidas: $fallos"
foreach($n in @('web1','web2','web3')) { Write-Host "  ${n}: $($conteo[$n])" }
Write-Host "Promedio (ms): $([math]::Round($tiempos/$Cantidad,2))"
$resultado=@{total=$Cantidad;exitos=($Cantidad-$fallos);fallos=$fallos;t_prom_ms=[math]::Round($tiempos/$Cantidad,2);distribucion=$conteo}
try {
 $body=ConvertTo-Json -InputObject $resultado -Depth 6 -Compress
 $null=Invoke-RestMethod -Uri "$base/api/pruebas" -Method Post -ContentType 'application/json' -Body ([System.Text.Encoding]::UTF8.GetBytes($body)) -TimeoutSec 10
 Write-Host 'Resultado guardado en MariaDB.'
} catch { Write-Warning "No se pudo guardar la prueba: $_" }
