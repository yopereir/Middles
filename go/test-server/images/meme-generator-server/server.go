package main

import (
    "os"
    "log"
    "fmt"
	"strconv"
	"math/rand"
    "net/http"
	"strings"
	"encoding/json"
    "github.com/filipkroca/revgeo"
	"context"
    "github.com/redis/go-redis/v9"
	"github.com/jmoiron/sqlx"
    _ "github.com/lib/pq"
)

const (
    TokenManagerURL = "tokenURL"
)
var (
    POSTGRES_DB = os.Getenv("POSTGRES_DB")
    POSTGRES_USER = os.Getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.Getenv("POSTGRES_PASSWORD")
)

func getMemes(query string, country string) (Meme){
    // Assign defaults if query or country does not exist
    _, exists := Memes[query]
    if !exists {
        query = "default"
    }
    _, exists = Memes[query][country]
    if !exists {
        country = "default"
    }
    log.Printf("Query: %s \nCountry: %s\n",query,country)

    // Get Meme from database
    fetchedMeme := Memes[query][country][rand.Intn(len(Memes[query][country]))]
    log.Printf("Title: %s\tURL: %s\tAltText: %s\n", fetchedMeme.Title, fetchedMeme.Url, fetchedMeme.AltText)
    return fetchedMeme
}

func canCallAPI(bearerToken string) bool {
    response, err := http.Get("https://"+TokenManagerURL+"?token="+bearerToken)
    if err != nil || response.StatusCode != http.StatusOK {
        return false
    }
    return true
}

func main() {
	// Init Redis
	ctx := context.Background()
	redisClient := redis.NewClient(&redis.Options{
		Addr: "redis:6379",
	})
    _, err := redisClient.Ping(ctx).Result()
    if err != nil {log.Printf("Error Connecting to redis: %s\n", err)} else {log.Println("Successfully connected to Redis!")}
	defer redisClient.Close()

	// Init Postgres
	dbClient, err := sqlx.Connect("postgres", "host=postgres port=5432 user="+POSTGRES_USER+" password="+POSTGRES_PASSWORD+" dbname="+POSTGRES_DB+" sslmode=disable")
    if err != nil {log.Printf("Error Connecting to Postgres: %s\n", err)} else {log.Println("Successfully connected to Postgres!")}
	defer dbClient.Close()

    http.HandleFunc("/", func (w http.ResponseWriter, r *http.Request) {
        fmt.Fprintf(w, "This is the meme generation server")
    })

    http.HandleFunc("/memes", func (w http.ResponseWriter, r *http.Request) {
        // Check if user can use API
        authHeader := r.Header.Get("Authorization")
        if authHeader == "" || strings.ToLower(strings.Fields(authHeader)[0]) != "bearer" || canCallAPI(strings.Fields(authHeader)[1]) {
            w.WriteHeader(http.StatusForbidden)
            w.Write([]byte("403 Forbidden - Access Denied"))
            return
        }

        // Sanitise data
        query := r.URL.Query().Get("query")
        lat, err := strconv.ParseFloat(r.URL.Query().Get("lat"), 64)
        lon, _ := strconv.ParseFloat(r.URL.Query().Get("lon"), 64)
        decoder := (revgeo.Decoder{})
        country, err := decoder.Geocode(lon, lat)
        if err != nil { country = ""}

        // Get meme
        response := getMemes(query, country)

        // Send Response
        w.Header().Set("Content-Type", "application/json")
        json.NewEncoder(w).Encode(response)
    })

    http.ListenAndServe(":8089", nil)
}