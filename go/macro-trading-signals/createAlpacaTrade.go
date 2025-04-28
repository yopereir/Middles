package main

import (
	"strings"
	"net/http"
	"io"
	"os"
	"fmt"
	"log"
)

func createAlpacaTrade(ticker string, tradeDirection string, quantity string, limitPrice string, orderType string) {
	// Validate inputs and secrets. example: ticker="AAPL", tradeDirection="buy", quantity="10", limitPrice="150.00"
	if orderType != "market" && orderType != "limit" {
		log.Fatal("Invalid order type. Must be 'market' or 'limit'.")
	}
	if ticker == "" || tradeDirection == "" || quantity == "" || (orderType == "limit" && limitPrice == "") {
		log.Fatal("Missing required parameters for Alpaca Trade.")
	}
	alpacaApiKey := os.Getenv("ALPACA_API_KEY")
	if alpacaApiKey == "" { log.Fatal("Missing ALPACA_API_KEY environment variable") }
	alpacaSecret := os.Getenv("ALPACA_API_SECRET")
	if alpacaSecret == "" { log.Fatal("Missing ALPACA_API_SECRET environment variable") }
	alpacaBaseUrl := os.Getenv("ALPACA_API_BASE_URL") // DEFAULT https://paper-api.alpaca.markets/v2
	if alpacaBaseUrl == "" { log.Fatal("Missing ALPACA_API_BASE_URL environment variable") }

	// Create request
	url := fmt.Sprintf("%s/orders", alpacaBaseUrl)
	payload := strings.NewReader("")
	if orderType == "market" {
		payload = strings.NewReader(fmt.Sprintf("{\"type\":\"market\",\"time_in_force\":\"gtc\",\"symbol\":\"%s\",\"qty\":\"%s\",\"side\":\"%s\"}",ticker,quantity,tradeDirection))
	} else {
		payload = strings.NewReader(fmt.Sprintf("{\"type\":\"limit\",\"time_in_force\":\"gtc\",\"symbol\":\"%s\",\"qty\":\"%s\",\"limit_price\":\"%s\",\"side\":\"%s\"}",ticker,quantity,limitPrice,tradeDirection))
	}
	req, _ := http.NewRequest("POST", url, payload)
	req.Header.Add("accept", "application/json")
	req.Header.Add("content-type", "application/json")
	req.Header.Add("APCA-API-KEY-ID", alpacaApiKey)
	req.Header.Add("APCA-API-SECRET-KEY", alpacaSecret)

	// Create Alpaca Trade
	fmt.Println("Creating Alpaca trade...")
	fmt.Println("Request URL: ", url)
	fmt.Println("Request Payload: ", payload)
	res, err := http.DefaultClient.Do(req)
	if err != nil {
		log.Printf("Error creating Alpaca trade:", err)
	}
	defer res.Body.Close()
	body, _ := io.ReadAll(res.Body)
	if res.StatusCode != 200 {
		log.Printf("Error creating Alpaca trade:", res.StatusCode, string(body))
	} else {
		fmt.Println("Alpaca trade created successfully:", string(body))
	}
}
