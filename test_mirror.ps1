$response = Invoke-RestMethod -Uri "http://localhost:8000/reflect" `
    -Method POST `
    -Headers @{"Content-Type" = "application/json"} `
    -Body '{"query":"The Spiral is complete"}'

$response | Format-List