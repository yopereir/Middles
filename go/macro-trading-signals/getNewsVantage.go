package main

import (
	"encoding/json"
	"fmt"
	"log"
	"io"
	"net/http"
	"os"
)

type NewsResponseFeedItemVantage struct {
    Title   string `json:"title"`
    Description string `json:"summary"`
}

type NewsResponseVantage struct {
    Articles []NewsResponseFeedItemVantage `json:"feed"`
}

func getNewsVantage() (NewsResponseVantage, error) {
	apiKey := os.Getenv("ALPHA_VANTAGE_KEY")
	if apiKey == "" {
		log.Fatal("Missing ALPHA_VANTAGE_KEY environment variable")
	}

	// Construct the URL with query parameters.
	url := fmt.Sprintf("https://www.alphavantage.co/query?function=NEWS_SENTIMENT&topics=mergers_and_acquisitions&apikey=%s", apiKey)

	// Make the GET request.
	resp, err := http.Get(url)
	if err != nil {
		fmt.Println("Error making request:", err)
		return NewsResponseVantage{}, err
	}
	defer resp.Body.Close()

	// Read the response body.
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		fmt.Println("Error reading response:", err)
		return NewsResponseVantage{}, err
	}

	// Unmarshal the JSON response into our struct.
	var newsResponseVantage NewsResponseVantage
	if err := json.Unmarshal(body, &newsResponseVantage); err != nil {
		fmt.Println("Error parsing JSON:", err)
		return NewsResponseVantage{}, err
	}
	return newsResponseVantage, nil
}
