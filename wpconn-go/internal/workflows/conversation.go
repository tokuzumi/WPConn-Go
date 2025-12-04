package workflows

import (
	"time"

	"go.temporal.io/sdk/temporal"
	"go.temporal.io/sdk/workflow"
	"wpconn-go/internal/activities"
	"wpconn-go/internal/domain"
)

func ConversationWorkflow(ctx workflow.Context) error {
	logger := workflow.GetLogger(ctx)
	logger.Info("Conversation workflow started")

	var a *activities.Activities // Pointer for activity registration reference

	// Setup activity options
	ao := workflow.ActivityOptions{
		StartToCloseTimeout: 10 * time.Second,
		RetryPolicy: &temporal.RetryPolicy{
			InitialInterval:    time.Second,
			BackoffCoefficient: 2.0,
			MaximumInterval:    time.Minute,
			MaximumAttempts:    5,
		},
	}
	ctx = workflow.WithActivityOptions(ctx, ao)

	// Channel to receive new messages
	messageChan := workflow.GetSignalChannel(ctx, "NewMessage")

	for {
		var msg domain.Message
		
		// Wait for signal
		selector := workflow.NewSelector(ctx)
		selector.AddReceive(messageChan, func(c workflow.ReceiveChannel, more bool) {
			c.Receive(ctx, &msg)
		})
		
		// Wait until a message is received
		selector.Select(ctx)

		logger.Info("Received message signal", "wamid", msg.Wamid, "type", msg.Type)

		// 1. Save Message (Processing)
		msg.Status = "processing"
		err := workflow.ExecuteActivity(ctx, a.SaveMessage, msg).Get(ctx, nil)
		if err != nil {
			logger.Error("Failed to save message", "error", err)
			continue // Continue loop even if save fails? Or retry? Activity has retry.
		}

		// 2. Check Media
		if msg.Type == "image" || msg.Type == "video" || msg.Type == "audio" || msg.Type == "document" || msg.Type == "sticker" {
			var mediaURL string
			err := workflow.ExecuteActivity(ctx, a.ResolveMediaUrl, msg.MetaMediaID).Get(ctx, &mediaURL)
			if err != nil {
				logger.Error("Failed to resolve media URL", "error", err)
				// Update status to failed?
				_ = workflow.ExecuteActivity(ctx, a.UpdateMessage, msg.Wamid, "", "failed_media").Get(ctx, nil)
				continue
			}

			// 3. Update Message (Received/Media Resolved)
			err = workflow.ExecuteActivity(ctx, a.UpdateMessage, msg.Wamid, mediaURL, "received").Get(ctx, nil)
			if err != nil {
				logger.Error("Failed to update message", "error", err)
			}
		} else {
			// Just text, update status to received
			err = workflow.ExecuteActivity(ctx, a.UpdateMessage, msg.Wamid, "", "received").Get(ctx, nil)
			if err != nil {
				logger.Error("Failed to update message", "error", err)
			}
		}
		
		// Future: Trigger AI Activity
	}
}
