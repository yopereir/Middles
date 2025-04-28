package main

import (
	"encoding/json"
	"context"
	"fmt"
	"log"
	"strings"
	"os"
	"github.com/google/generative-ai-go/genai"
	"google.golang.org/api/option"
)

type TradeSignal struct {
	Direction       string    `json:"tradeDirection"`
	Ticker       string    `json:"tickerSymbol"`
	BuyPrice       string    `json:"buyPrice"`
	SellPrice       string    `json:"sellPrice"`
}

func getInference(newsArticle string, modelToUse string) (TradeSignal, error) {
	ctx := context.Background()
	if newsArticle == "" {
		log.Fatal("Missing news article.")
	}
	if modelToUse == "" {
		modelToUse = "gemini-pro" // Choose your model
	}

	// Replace with your actual API key
	apiKey := os.Getenv("GOOGLE_API_KEY")
	if apiKey == "" {
		log.Fatal("Missing GOOGLE_API_KEY environment variable")
	}

	client, err := genai.NewClient(ctx, option.WithAPIKey(apiKey))
	if err != nil {
		log.Fatal(err)
	}
	defer client.Close()

	model := client.GenerativeModel(modelToUse)  // Choose your model
	// Trade on M&A news
	//promptResponseDefinition := "Trade signal should be a json object having the following keys: tradeDirection, tickerSymbol, buyPrice, sellPrice. tradeDirection should be 'buy' if it is bullish news or 'sell' if it is bearish news for the company being bought. Ticket symbol is only the symbol of the company being bought. All values in the JSON will be a string. If you are less than 50 percent confident about a value enter 'unsure' as the string. If no information can be got from the news article enter unsure for all fields. Your output should only be in json format."
	// Trade on M&A news- refined1
	//promptResponseDefinition := "Trade signal should be a json object having only the following keys: tradeDirection, tickerSymbol, buyPrice, sellPrice. The trade signal is for merger and acquisition news. The tradeDirection should be 'buy' if acquisition price for the company being bought is higher than its market cap or 'sell' if acquisition price for the company being bought is lower than its market cap. The ticker symbol is only the symbol of the company being bought. All values in the JSON will be a string. If you are less than 50 percent confident about a value enter 'unsure' as the string. If no information can be got from the news article enter unsure for all fields. Your output should only be in json format."
	// Trade on M&A news- refined2
	//promptResponseDefinition := "Trade signal should be a json object having only the following keys: tradeDirection, tickerSymbol, buyPrice, sellPrice. The trade signal is for merger and acquisition news. The tradeDirection should be 'buy' if it is positive news for the company being acquired or 'sell' if it is negative news. The ticker symbol is only for the symbol of the company being acquired. All values in the JSON will be a string. If you are less than 50 percent confident about a value or there is no information available, enter 'unsure' as the string. Your output should only be in json format."
	// Trade on all news
	promptResponseDefinition := "Trade signal should be a json object having only the following keys: tradeDirection, tickerSymbol, buyPrice, sellPrice. The trade signal is for whether to buy or sell a company stock. The tradeDirection should be 'buy' if it is positive news for the company stock or 'sell' if it is negative news. If there are multiple signals for multiple companies, only return 1 signal that you are most confident about. All values in the JSON will be a string. If you are not confident about a value or there is no information available, enter 'unsure' as the string. Your output should only be in json format."
	prompt := "Read the following news and generate a trade signal and nothing else." + promptResponseDefinition + "News: \n" + newsArticle

	resp, err := model.GenerateContent(ctx, genai.Text(prompt))
	if err != nil {
		log.Fatal(err)
	}

	jsonString := string(resp.Candidates[0].Content.Parts[0].(genai.Text))
	var tradeSignal TradeSignal

	// Sanitize the JSON string to remove any unwanted characters or formatting
	jsonString = strings.TrimSpace(jsonString)
	jsonString = strings.TrimPrefix(jsonString, "```json")
	jsonString = strings.TrimSuffix(jsonString, "```")
    jsonString = strings.TrimSuffix(jsonString, "json")  // handle case where "json" suffix remains
	jsonString = strings.TrimSpace(jsonString)  // Trim again after removing prefixes/suffixes

	if err := json.Unmarshal([]byte(jsonString), &tradeSignal); err != nil {
		fmt.Println("Error parsing JSON:", err)
		return TradeSignal{}, err
	}

	return tradeSignal, nil
}