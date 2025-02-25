package main

import (
    "os"
    "log"
    "fmt"
	"strconv"
	"math/rand"
    "net/http"
	"strings"
    "time"
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

func getSpicyAIMemes(query string, country string) (Meme){
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

    // Generate AI meme
    fetchedMeme := Memes[query][country][rand.Intn(len(Memes[query][country]))]
    log.Printf("Title: %s\tURL: %s\tAltText: %s\n", fetchedMeme.Title, fetchedMeme.Url, fetchedMeme.AltText)
    return fetchedMeme
}

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

    // Get Meme from Struct OR Database
    fetchedMeme := Memes[query][country][rand.Intn(len(Memes[query][country]))]
    log.Printf("Title: %s\tURL: %s\tAltText: %s\n", fetchedMeme.Title, fetchedMeme.Url, fetchedMeme.AltText)
    return fetchedMeme
}

func getSubscriptionTypeAndDeductBalance(bearerToken string) (string, error) {
	// Init Redis
	ctx := context.Background()
	redisClient := redis.NewClient(&redis.Options{Addr: "redis:6379",})
    _, err := redisClient.Ping(ctx).Result()
    if err != nil {
        log.Printf("Error Connecting to redis: %s\n", err)
        return "", err
    } else {
        log.Println("Successfully connected to Redis!")
    }
	defer redisClient.Close()

	// Init Postgres
	dbClient, err := sqlx.Connect("postgres", "host=postgres port=5432 user="+POSTGRES_USER+" password="+POSTGRES_PASSWORD+" dbname="+POSTGRES_DB+" sslmode=disable")
    if err != nil {
        log.Printf("Error Connecting to Postgres: %s\n", err)
        return "", err
    } else {
        log.Println("Successfully connected to Postgres!")
    }
	defer dbClient.Close()

    // Get User Data
    // Get userID 
    //  response, err := http.Get("https://"+TokenManagerURL+"?token="+bearerToken)
    //  if err != nil || response.StatusCode != http.StatusOK {return "", err}
	//  defer response.Body.Close()
    //  var result map[string]string
    //  if err:= json.NewDecoder(response.Body).Decode(&result); err !=nil {return "", err}
    //  userID := result["userId"]
    userID := "user1" // Mock data

    // Get currentBalance
    var currentBalance int
    // Check if userBalance is present on Redis
	userBalance, err := redisClient.Get(ctx, "token:"+bearerToken).Result()
    if err == redis.Nil {
        // Get userBalance from Postgres if not present in Redis
        var fetchedBalance int
        err := dbClient.QueryRow("SELECT tokenBalance FROM users WHERE userID = $1", userID).Scan(&fetchedBalance)
        if err != nil {return "", err}
        userBalance = fmt.Sprintf("%d", fetchedBalance)
        // Set Balance in Redis
        err = redisClient.Set(ctx, "token:"+bearerToken, userBalance, time.Hour).Err()
        if err != nil {return "", err}
    }
    currentBalance, err = strconv.Atoi(userBalance)
    if err != nil {return "", err}

    // Get subscriptionType
    // Check if subscriptionType is present on Redis
	subscriptionType, err := redisClient.Get(ctx, "subscription:"+bearerToken).Result()
    if err == redis.Nil {
        // Get subscriptionType from Postgres if not present in Redis
        var fetchedSubscriptionType string
        err := dbClient.QueryRow("SELECT subscriptionType FROM users WHERE userID = $1", userID).Scan(&fetchedSubscriptionType)
        if err != nil {return "", err}
        subscriptionType = fetchedSubscriptionType
        // Set Balance in Redis
        err = redisClient.Set(ctx, "subscription:"+bearerToken, subscriptionType, time.Hour).Err()
        if err != nil {return "", err}
    }
    
    // Deduct Balance
    if subscriptionType == "AI" {
        currentBalance -= 3
    } else {
        currentBalance -= 1
    }
    // Deduct Balance in redis
    err = redisClient.Set(ctx, "token:"+bearerToken, userBalance, time.Hour).Err()
    if err != nil {return subscriptionType, err}
    // Deduct Balance from Postgres asynchronously
    go func () {
        _, err = dbClient.Exec("UPDATE users SET tokenBalance = $1 where userID = $2",currentBalance,userID)
        if err != nil {log.Printf("Error updating the Postgres database with user data:\nuserID: "+userID+"\ntokenBalance: "+fmt.Sprintf("%d",currentBalance))}
    }()
    return subscriptionType, nil
}

func main() {
    http.HandleFunc("/", func (w http.ResponseWriter, r *http.Request) {
        fmt.Fprintf(w, "This is the meme generation server")
    })

    http.HandleFunc("/memes", func (w http.ResponseWriter, r *http.Request) {
        // Check if user can use API
        authHeader := r.Header.Get("Authorization")
        if authHeader == "" || strings.ToLower(strings.Fields(authHeader)[0]) != "bearer" {
            http.Error(w, "403 Forbidden - Access Denied", http.StatusForbidden)
            return
        }
        
        subscriptionType, err := getSubscriptionTypeAndDeductBalance(strings.Fields(authHeader)[1])
        if err != nil {
            http.Error(w, fmt.Sprintf("500 Internal Server Error - %s",err), http.StatusInternalServerError)
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
        var response Meme
        if subscriptionType == "AI" {
            response = getSpicyAIMemes(query, country)
        } else {
            response = getMemes(query, country)
        }

        // Send Response
        w.Header().Set("Content-Type", "application/json")
        json.NewEncoder(w).Encode(response)
    })

    http.ListenAndServe(":8089", nil)
}