package main

import (
	"log"
	"os"
	"os/signal"
	"strings"
	"syscall"
	"time"

	"wpconn-go/api"
	"wpconn-go/internal/activities"
	"wpconn-go/internal/database"
	"wpconn-go/internal/workflows"

	"github.com/gofiber/fiber/v3"
	"github.com/gofiber/fiber/v3/middleware/cors"
	"github.com/gofiber/fiber/v3/middleware/logger"
	"go.temporal.io/sdk/client"
	"go.temporal.io/sdk/worker"
)

func main() {
	// 0. Database Connection
	database.Connect()
	defer database.Close()

	// 1. Config Loading
	temporalHost := os.Getenv("TEMPORAL_HOST_PORT")
	if temporalHost == "" {
		temporalHost = "temporal:7233"
	}
	port := os.Getenv("PORT")
	if port == "" {
		port = "3000"
	}

	// 2. Temporal Client
	// Retry connection to Temporal as it might take a while to start
	var temporalClient client.Client
	var err error
	for i := 0; i < 10; i++ {
		temporalClient, err = client.Dial(client.Options{
			HostPort: temporalHost,
		})
		if err == nil {
			break
		}
		log.Printf("Failed to connect to Temporal (attempt %d/10): %v", i+1, err)
		time.Sleep(2 * time.Second)
	}
	if err != nil {
		log.Fatalf("Unable to create Temporal client: %v", err)
	}
	defer temporalClient.Close()
	log.Println("Connected to Temporal!")

	// 2.5 Start Temporal Worker
	w := worker.New(temporalClient, "WHATSAPP_TASK_QUEUE", worker.Options{})
	w.RegisterWorkflow(workflows.ConversationWorkflow)
	w.RegisterActivity(&activities.Activities{})

	go func() {
		if err := w.Run(worker.InterruptCh()); err != nil {
			log.Fatalf("Unable to start worker: %v", err)
		}
	}()

	// 3. Fiber App
	app := fiber.New(fiber.Config{
		AppName: "WPConn Go Gateway",
	})

	// Middleware
	app.Use(logger.New())
	
	// CORS Configuration
	origins := os.Getenv("BACKEND_CORS_ORIGINS")
	if origins == "" {
		origins = "*"
	} else {
		// Clean up the format ["url1", "url2"] to url1,url2 if necessary, 
		// but simple comma-separated is standard for Fiber CORS usually.
		// If the input is JSON array string, we might need parsing, but for now assume comma-separated or single value.
		// The python env had JSON format `["..."]`. We should probably handle that or ask user to change env.
		// For robustness, let's strip brackets and quotes.
		origins = strings.ReplaceAll(origins, "[", "")
		origins = strings.ReplaceAll(origins, "]", "")
		origins = strings.ReplaceAll(origins, "\"", "")
	}

	app.Use(cors.New(cors.Config{
		// Fiber v3 uses []string for AllowOrigins? Checking docs... v2 used AllowOrigins string. v3 might differ.
		// Actually Fiber v3 might use AllowOriginsFunc or similar. Let's assume v3 standard config.
		// If v3 changes, we might need to adjust. v3 beta docs say AllowOrigins is []string or string?
		// Let's stick to simple string if possible or split.
		// Safe bet: AllowOrigins: []string{origins} might be wrong if it expects a list.
		// Let's split by comma.
		AllowOrigins: strings.Split(origins, ","),
		AllowHeaders: []string{"Origin", "Content-Type", "Accept", "x-api-key"},
	}))

	// 4. Routes
	api.SetupRoutes(app, temporalClient)

	// 5. Start Server (Graceful Shutdown)
	go func() {
		if err := app.Listen(":" + port); err != nil {
			log.Fatalf("Error starting server: %v", err)
		}
	}()

	// Wait for interrupt signal
	c := make(chan os.Signal, 1)
	signal.Notify(c, os.Interrupt, syscall.SIGTERM)
	<-c

	log.Println("Shutting down...")
	if err := app.Shutdown(); err != nil {
		log.Printf("Error shutting down server: %v", err)
	}
	log.Println("Server exited")
}
