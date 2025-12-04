package database

import (
	"context"
	"log"
	"os"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
)

var Pool *pgxpool.Pool

func Connect() {
	dbURL := os.Getenv("DATABASE_URL")
	if dbURL == "" {
		log.Fatal("DATABASE_URL is not set")
	}

	config, err := pgxpool.ParseConfig(dbURL)
	if err != nil {
		log.Fatalf("Unable to parse DATABASE_URL: %v", err)
	}

	// Connection pool settings
	config.MaxConns = 80
	config.MinConns = 2
	config.MaxConnLifetime = time.Hour
	config.MaxConnIdleTime = 30 * time.Minute

	// Retry connection
	for i := 0; i < 10; i++ {
		Pool, err = pgxpool.NewWithConfig(context.Background(), config)
		if err == nil {
			// Test connection
			if err := Pool.Ping(context.Background()); err == nil {
				log.Println("Connected to PostgreSQL!")
				return
			}
		}
		log.Printf("Failed to connect to Postgres (attempt %d/10): %v", i+1, err)
		time.Sleep(2 * time.Second)
	}

	log.Fatalf("Could not connect to PostgreSQL after retries")
}

func Close() {
	if Pool != nil {
		Pool.Close()
	}
}
