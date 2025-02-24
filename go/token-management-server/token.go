package token

import (
    "fmt"
	"strconv"
    "net/http"
	"encoding/json"
)

func main() {
    http.HandleFunc("/", func (w http.ResponseWriter, r *http.Request) {
        fmt.Fprintf(w, "Wewlcome to my website!")
        token := r.URL.Query().Get("token")
        lat, err := strconv.ParseFloat(r.URL.Query().Get("lat"), 64)
        lon, _ := strconv.ParseFloat(r.URL.Query().Get("lon"), 64)

		w.WriteHeader(http.StatusForbidden)
		w.Write([]byte("403 Forbidden - Access Denied"))

        w.Header().Set("Content-Type", "application/json")
        json.NewEncoder(w).Encode(response)
    })
}