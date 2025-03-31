package main
import (
	"log"
	"fmt"
	"github.com/joho/godotenv"
)

func getTradeSignalsFromSpecificNewsArticle(articleText string) {
	if articleText =="" {
		log.Fatal("Missing news article.")
	}
	tradeSignal, err := getInference(articleText, "gemini-2.0-flash")
	if err != nil {
		log.Fatal("Error getting inference:", err)
	}
	fmt.Println("Ticker: ", tradeSignal.Ticker)
	fmt.Println("Trade Direction: ", tradeSignal.Direction)
}

func getTradeSignalsFromNews() {
	newsResponse, err := getNews()
	if err != nil {
		log.Fatal("Error getting news responses:", err)
	}
	for _, article := range newsResponse.Articles {
		tradeSignal, err := getInference(article.Description, "gemini-2.0-flash")
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
	getTradeSignalsFromSpecificNewsArticle("IBM in talks to buy Target for 19 billion, 15 percent discount on market cap")
	// Below function will call newsAPI to get the latest news and then call the AI model to get the trade signals for each news article.
	//getTradeSignalsFromNews()
}
