package main

import (
	"fmt"
	"log"
	"github.com/joho/godotenv"
)

func getTradeSignalsFromSpecificNewsArticle(articleText string) (TradeSignal, error) {
	if articleText =="" {
		log.Fatal("Missing news article.")
	}
	tradeSignal, err := getInference(articleText, "gemma-3-27b-it")
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

func main() {
	err := godotenv.Load()
	if err != nil {
		log.Fatal("Error loading .env file")
	}
	// Test function to call the AI model with a specific news article
	//tradeSignal, _ := getTradeSignalsFromSpecificNewsArticle("Merck (NSE:PROR) KGaA has struck a deal to buy U.S. biotech company SpringWorks Therapeutics for an equity value of $3.9 billion, as the German company seeks to acquire treatments for rare tumours to boost its cancer drugs business. The family-controlled company said in a statement on Monday the purchase price of $47 per share in cash represents an equity value of about $3.9 billion, or an enterprise value of $3.4 billion (3 billion euros), when SpringWorks’ cash holdings are deducted.")
	// Below function will call newsAPI to get the latest news and then call the AI model to get the trade signals for each news article.
	//getTradeSignalsFromNews() // Get news from NewsAPI
	//getTradeSignalsFromNewsVantage() // Get news from NewsVantage API
	//if tradeSignal.Ticker != "unsure" {
	//	createAlpacaTrade(tradeSignal.Ticker, tradeSignal.Direction, "10", "20.00", "limit") // limit order example
		//createAlpacaTrade(tradeSignal.Ticker, tradeSignal.Direction, "100", "150.00", "market") // market order example
	//}
	listenWebsocketAlpaca()
}
