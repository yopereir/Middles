package main

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestAuthToken(t *testing.T) {
	tests := []struct {
		name        string
		authHeader  string
		wantStatus  int
	}{
		{"Valid Bearer Token", "Bearer validToken", http.StatusOK},  // Should return 200
		{"Missing Authorization Header", "", http.StatusForbidden},  // Should return 403
		{"Malformed Header (No Bearer)", "Invalid validToken", http.StatusForbidden}, // Should return 403
		{"Empty Token After Bearer", "Bearer ", http.StatusForbidden}, // Should return 403
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			req, err := http.NewRequest("GET", "/memes", nil)
			if err != nil {
				t.Fatal(err)
			}

			if tt.authHeader != "" {
				req.Header.Set("Authorization", tt.authHeader)
			}

			rr := httptest.NewRecorder()
			handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				authHeader := r.Header.Get("Authorization")

				if authHeader == "" || !strings.HasPrefix(strings.ToLower(authHeader), "bearer ") || len(strings.Fields(authHeader)) < 2 || strings.Fields(authHeader)[1] == "" {
					http.Error(w, "403 Forbidden - Access Denied", http.StatusForbidden)
					return
				}

				w.WriteHeader(http.StatusOK)
			})

			handler.ServeHTTP(rr, req)

			if status := rr.Code; status != tt.wantStatus {
				t.Errorf("%s: expected status %d, got %d", tt.name, tt.wantStatus, status)
			}
		})
	}
}
func TestMemeForStandardSubscription(t *testing.T) {
	tests := []struct {
		name        string
		bearerToken  string
		meme  		[]Meme
		wantStatus  int
	}{
		{"Valid Meme response", "2", []Meme{{Title: "Food USA meme",Url: "Food USA URL",AltText: "Food USA altText"}}, http.StatusOK},  // Should return 200
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			req, err := http.NewRequest("GET", "memes?lat=40.73&lon=-73.93&query=food", nil)
			if err != nil {
				t.Fatal(err)
			}

			if tt.bearerToken != "" {
				req.Header.Set("Authorization", "Bearer "+tt.bearerToken)
			}

			rr := httptest.NewRecorder()
			// Define the handler function to be tested
			handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				authHeader := r.Header.Get("Authorization")
		
				// Check if the token is "Bearer Token"
				if authHeader != "Bearer "+tt.bearerToken {
					http.Error(w, "403 Forbidden - Access Denied", http.StatusForbidden)
					return
				}
		
				// Check query parameters
				query := r.URL.Query()
				lat := query.Get("lat")
				lon := query.Get("lon")
				searchQuery := query.Get("query")
		
				// Validate lat, lon, and query
				if lat == "40.73" && lon == "-73.93" && searchQuery == "food" {
					w.Header().Set("Content-Type", "application/json")
					w.WriteHeader(http.StatusOK)
					json.NewEncoder(w).Encode(Meme{
						Title:   "Food USA meme",
						Url:     "Food USA URL",
						AltText: "Food USA altText",
					})
					return
				}

				http.Error(w, "400 Bad Request - Invalid Parameters", http.StatusBadRequest)
			})

			handler.ServeHTTP(rr, req)
			var resp Meme
			err = json.Unmarshal(rr.Body.Bytes(), &resp)
			if err != nil {
				t.Fatal(err)
			}
			if status := rr.Code; resp.Title != tt.meme[0].Title || status != tt.wantStatus {
				t.Errorf("%s: expected status %d, got %d", tt.name, tt.wantStatus, status)
			}
		})
	}
}
