
# Simple Hurl session to validate VISE API

# Health
GET {{host}}/health
HTTP/1.1 200
jsonpath "$.status" == "ok"

# Register Platinum OK
POST {{host}}/client
[Captures]
jsonpath "$.clientId" as client_platinum
[Headers]
content-type: application/json
[Body]
{
  "name": "John Doe",
  "country": "USA",
  "monthlyIncome": 1200,
  "viseClub": true,
  "cardType": "Platinum"
}
HTTP/1.1 200
jsonpath "$.status" == "Registered"
jsonpath "$.cardType" == "Platinum"

# Purchase with Saturday 30% (amount > 200)
# Use a fixed Saturday date: 2025-09-20 is a Saturday
POST {{host}}/purchase
[Headers]
content-type: application/json
[Body]
{
  "clientId": {{client_platinum}},
  "amount": 250,
  "currency": "USD",
  "purchaseDate": "2025-09-20T14:30:00Z",
  "purchaseCountry": "France"
}
HTTP/1.1 200
jsonpath "$.status" == "Approved"
jsonpath "$.purchase.finalAmount" == 175
jsonpath "$.purchase.benefit" contains "30%"

# Register Black rejected by residency
POST {{host}}/client
[Headers]
content-type: application/json
[Body]
{
  "name": "Alice",
  "country": "India",
  "monthlyIncome": 3000,
  "viseClub": true,
  "cardType": "Black"
}
HTTP/1.1 400
jsonpath "$.status" == "Rejected"

# Register Black OK (USA)
POST {{host}}/client
[Captures]
jsonpath "$.clientId" as client_black
[Headers]
content-type: application/json
[Body]
{
  "name": "Bob",
  "country": "USA",
  "monthlyIncome": 3000,
  "viseClub": true,
  "cardType": "Black"
}
HTTP/1.1 200
jsonpath "$.status" == "Registered"

# Purchase rejected by purchaseCountry restriction for Black
POST {{host}}/purchase
[Headers]
content-type: application/json
[Body]
{
  "clientId": {{client_black}},
  "amount": 150,
  "currency": "USD",
  "purchaseDate": "2025-09-22T10:00:00Z",
  "purchaseCountry": "China"
}
HTTP/1.1 400
jsonpath "$.status" == "Rejected"
jsonpath "$.error" contains "no puede realizar compras"
