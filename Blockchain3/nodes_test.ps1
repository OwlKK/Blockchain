# Define the URL of the blockchain server
$Url = "http://127.0.0.1:5000/nodes/register"

# Define the JSON payload with the nodes
$Body = @{
    nodes = @("http://127.0.0.1:5002", "http://127.0.0.1:5001")
} | ConvertTo-Json -Depth 10

# Send the POST request to the server
$response = Invoke-RestMethod -Uri $Url -Method POST -Body $Body -ContentType "application/json"

# Output the response
$response