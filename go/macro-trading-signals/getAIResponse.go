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
	//promptResponseDefinition := "Trade signal should be a json object having the following keys: tradeDirection, tickerSymbol, buyPrice, sellPrice. tradeDirection should be 'buy' if it is bullish news or 'sell' if it is bearish news for the company being bought. Ticket symbol is only the symbol of the company being bought. All values in the JSON will be a string. If you are less than 50 percent confident about a value enter 'unsure' as the string. If no information can be got from the news article enter unsure for all fields. Your output should only be in json format."
	promptResponseDefinition := "Trade signal should be a json object having only the following keys: tradeDirection, tickerSymbol, buyPrice, sellPrice. The trade signal is for merger and acquisition news. The tradeDirection should be 'buy' if acquisition price for the company being bought is higher than its market cap or 'sell' if acquisition price for the company being bought is lower than its market cap. The ticker symbol is only the symbol of the company being bought. All values in the JSON will be a string. If you are less than 50 percent confident about a value enter 'unsure' as the string. If no information can be got from the news article enter unsure for all fields. Your output should only be in json format."
	prompt := "Read the following news and generate a trade signal and nothing else." + promptResponseDefinition + "News: \n" + newsArticle

	resp, err := model.GenerateContent(ctx, genai.Text(prompt))
	if err != nil {
		log.Fatal(err)
	}

	fmt.Println("Generated Text:")
	for _, part := range resp.Candidates[0].Content.Parts {
		fmt.Println(part)
	}
	jsonString := string(resp.Candidates[0].Content.Parts[0].(genai.Text))
	var tradeSignal TradeSignal

	// Sanitize the JSON string to remove any unwanted characters or formatting
	fmt.Println("Raw JSON Response:", jsonString)
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