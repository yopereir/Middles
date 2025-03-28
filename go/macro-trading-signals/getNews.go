package main

import (
	"encoding/json"
	"fmt"
	"log"
	"io"
	"net/http"
	"os"
)

type NewsResponse struct {
	Status       string    `json:"status"`
	TotalResults int       `json:"totalResults"`
	Articles     []Article `json:"articles"`
}

type Article struct {
	Source      Source `json:"source"`
	Author      string `json:"author"`
	Title       string `json:"title"`
	Description string `json:"description"`
	URL         string `json:"url"`
	PublishedAt string `json:"publishedAt"`
}

type Source struct {
	ID   string `json:"id"`
	Name string `json:"name"`
}

func getNews(API_KEY string) {
	apiKey := os.Getenv("NEWS_API_KEY")
	if apiKey == "" {
		log.Fatal("Missing NEWS_API_KEY environment variable")
	}

	// Construct the URL with query parameters.
	url := fmt.Sprintf("https://newsapi.org/v2/top-headlines?country=us&apiKey=%s", API_KEY)

	// Make the GET request.
	resp, err := http.Get(url)
	if err != nil {
		fmt.Println("Error making request:", err)
		return
	}
	defer resp.Body.Close()

	// Read the response body.
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		fmt.Println("Error reading response:", err)
		return
	}

	// Unmarshal the JSON response into our struct.
	var newsResponse NewsResponse
	if err := json.Unmarshal(body, &newsResponse); err != nil {
		fmt.Println("Error parsing JSON:", err)
		return
	}

	// Print out the fetched news details.
	fmt.Printf("Status: %s\n", newsResponse.Status)
	fmt.Printf("Total Results: %d\n", newsResponse.TotalResults)
	for i, article := range newsResponse.Articles {
		fmt.Printf("\nArticle %d:\n", i+1)
		fmt.Printf("Title: %s\n", article.Title)
		fmt.Printf("Description: %s\n", article.Description)
		fmt.Printf("URL: %s\n", article.URL)
	}
}
