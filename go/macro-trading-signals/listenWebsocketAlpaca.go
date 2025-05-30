package main

import (
    "fmt"
    "log"
    "os"
    "os/signal"
    "time"
	"encoding/json"
    "github.com/gorilla/websocket"
)
type AuthMessage struct {
	Action string `json:"action"`
	Key    string `json:"key"`
	Secret string `json:"secret"`
}

type SubscriptionMessage struct {
	Action string   `json:"action"`
	News   []string `json:"news"`
}
type NewsMessage struct {
	T        string   `json:"T"`
	Headline string   `json:"headline"`
	Summary  string   `json:"summary"`
	Content  string   `json:"content"`
	Symbols  []string `json:"symbols"`
}
func connectAndListen(apiKey, apiSecret string, done chan struct{}) {
	for {
		err := connectOnce(apiKey, apiSecret, done)
		if err != nil {
			log.Printf("Connection error: %v. Reconnecting...", err)
		}

		select {
		case <-done:
			log.Println("Received done signal, stopping reconnect attempts.")
			return
		default:
			// Sleep before reconnect attempt
			time.Sleep(2 * time.Second)
		}
	}
}

func connectOnce(apiKey, apiSecret string, done chan struct{}) error {
	alpacaWebsocketUrl := os.Getenv("ALPACA_WEBSOCKET_URL") // DEFAULT: wss://stream.data.alpaca.markets/v1beta1/news
	if alpacaWebsocketUrl == "" { log.Fatal("Missing ALPACA_WEBSOCKET_URL environment variable") }

	log.Printf("Connecting to %s", alpacaWebsocketUrl)

	c, _, err := websocket.DefaultDialer.Dial(alpacaWebsocketUrl, nil)
	if err != nil {
		return fmt.Errorf("dial error: %w", err)
	}
	defer c.Close()

	// Authenticate
	auth := AuthMessage{
		Action: "auth",
		Key:    apiKey,
		Secret: apiSecret,
	}
	if err := c.WriteJSON(auth); err != nil {
		return fmt.Errorf("auth write error: %w", err)
	}

	// Subscribe to all news
	sub := SubscriptionMessage{
		Action: "subscribe",
		News:   []string{"*"},
	}
	if err := c.WriteJSON(sub); err != nil {
		return fmt.Errorf("subscribe write error: %w", err)
	}

	// Start reading messages
	for {
		_, message, err := c.ReadMessage()
		if err != nil {
			return fmt.Errorf("read message error: %w", err)
		}
		handleMessage(message)
	}
}
func handleMessage(message []byte) {
	// You can unmarshal into structs if needed
	log.Printf("Received: %s", message)
	var newsItems []NewsMessage
	err := json.Unmarshal(message, &newsItems)
	if err != nil {
		log.Printf("Failed to unmarshal message: %v", err)
		return
	}
	for _, news := range newsItems {
		log.Printf("News: [T=%s] Headline=%s Summary=%s Symbols=%v",
			news.T, news.Headline, news.Summary, news.Symbols)
		if news.T == "n" {makeTrade(news)}
	}
	
}

func makeTrade(newsItem NewsMessage){
	tradeSignal, _ := getTradeSignalsFromSpecificNewsArticle("Headline: " + newsItem.Headline + "Summary: " + newsItem.Summary + "Content: " + newsItem.Content)
	log.Printf("Trade signal from AI:\nTicker: " + tradeSignal.Ticker + "\nDirection: " + tradeSignal.Direction)
	if tradeSignal.Ticker != "unsure" && tradeSignal.Direction != "unsure" {
		//createAlpacaTrade(tradeSignal.Ticker, tradeSignal.Direction, "10", "0.03", "limit") // limit order example
		createAlpacaTrade(tradeSignal.Ticker, tradeSignal.Direction, "100", "150.00", "market") // market order example
	}
}

func listenWebsocketAlpaca() {
	alpacaApiKey := os.Getenv("ALPACA_API_KEY")
	if alpacaApiKey == "" { log.Fatal("Missing ALPACA_API_KEY environment variable") }
	alpacaSecret := os.Getenv("ALPACA_API_SECRET")
	if alpacaSecret == "" { log.Fatal("Missing ALPACA_API_SECRET environment variable") }

	// Initialize interrupt signal
	interrupt := make(chan os.Signal, 1)
	signal.Notify(interrupt, os.Interrupt)
	done := make(chan struct{})

	go connectAndListen(alpacaApiKey, alpacaSecret, done)

	// Wait for interrupt signal to gracefully shutdown
	<-interrupt
	log.Println("Interrupt signal received, shutting down...")
	close(done)
	time.Sleep(1 * time.Second) // Give time for goroutines to cleanup
}