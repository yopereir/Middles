package main
import (
	"context"
	"fmt"
	"log"
	"os"
	"github.com/google/generative-ai-go/genai"
	"google.golang.org/api/option"
)

func getInference() {
	ctx := context.Background()

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

	model := client.GenerativeModel("gemini-pro")  // Choose your model
	prompt := "Write a short poem about the sea."

	resp, err := model.GenerateContent(ctx, genai.Text(prompt))
	if err != nil {
		log.Fatal(err)
	}

	fmt.Println("Generated Text:")
	for _, part := range resp.Candidates[0].Content.Parts {
		fmt.Println(part)
	}
}