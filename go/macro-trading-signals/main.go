package main

import (
	"fmt"
	"log"
	"strings"
	"net/http"
	"io"
	"os"
	"github.com/joho/godotenv"
)

func getTradeSignalsFromSpecificNewsArticle(articleText string) (TradeSignal, error) {
	if articleText =="" {
		log.Fatal("Missing news article.")
	}
	tradeSignal, err := getInference(articleText, "gemini-2.0-flash")
	if err != nil {
		log.Fatal("Error getting inference:", err)
	}
	fmt.Println("Ticker: ", tradeSignal.Ticker)
	fmt.Println("Trade Direction: ", tradeSignal.Direction)
	return tradeSignal, nil
}

func getTradeSignalsFromNews() {
	newsResponse, err := getNews()
	if err != nil {
		log.Fatal("Error getting news responses:", err)
	}
	for _, article := range newsResponse.Articles {
		tradeSignal, err := getInference(article.Title, "gemini-2.0-flash")
		if err != nil {
			log.Fatal("Error getting inference:", err)
		}
		fmt.Println("Title: ", article.Title)
		fmt.Println("Ticker: ", tradeSignal.Ticker)
		fmt.Println("Trade Direction: ", tradeSignal.Direction)
	}
}

func getTradeSignalsFromNewsVantage() {
	newsResponse, err := getNewsVantage()
	if err != nil {
		log.Fatal("Error getting news responses:", err)
	}
	for _, article := range newsResponse.Articles {
		tradeSignal, err := getInference(article.Title, "gemini-2.0-flash")
		if err != nil {
			log.Fatal("Error getting inference:", err)
		}
		fmt.Println("Title: ", article.Title)
		fmt.Println("Ticker: ", tradeSignal.Ticker)
		fmt.Println("Trade Direction: ", tradeSignal.Direction)
	}
}

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
	alpacaBaseUrl := os.Getenv("ALPACA_API_BASE_URL")
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
		log.Fatal("Error creating Alpaca trade:", err)
	}
	defer res.Body.Close()
	body, _ := io.ReadAll(res.Body)
	if res.StatusCode != 200 {
		log.Fatal("Error creating Alpaca trade:", res.StatusCode, string(body))
	} else {
		fmt.Println("Alpaca trade created successfully:", string(body))
	}
}

func main() {
	err := godotenv.Load()
	if err != nil {
		log.Fatal("Error loading .env file")
	}
	// Test function to call the AI model with a specific news article
	tradeSignal, _ := getTradeSignalsFromSpecificNewsArticle("Mr. Cooper Group Inc. COOP and Rocket Companies, Inc. RKT have jointly announced an agreement under which the former will be acquired by the latter in an all-stock deal valued at $9.4 billion. This will create a mortgage behemoth in the United States, with the combined firm servicing $2.1 trillion of loans and 9.5 million clients.")
	// Below function will call newsAPI to get the latest news and then call the AI model to get the trade signals for each news article.
	//getTradeSignalsFromNews() // Get news from NewsAPI
	//getTradeSignalsFromNewsVantage() // Get news from NewsVantage API
	if tradeSignal.Ticker != "unsure" {
		createAlpacaTrade(tradeSignal.Ticker, tradeSignal.Direction, "10", "20.00", "limit") // limit order example
		//createAlpacaTrade(tradeSignal.Ticker, tradeSignal.Direction, "100", "150.00", "market") // market order example
	}
}
