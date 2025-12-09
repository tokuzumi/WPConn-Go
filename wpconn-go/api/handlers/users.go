package handlers

import (
	"context"
	"time"
	"wpconn-go/internal/database"
	"wpconn-go/internal/domain"

	"github.com/gofiber/fiber/v3"
	"golang.org/x/crypto/bcrypt"
)

// GetUsers lists all users
func GetUsers(c fiber.Ctx) error {
	ctx := context.Background()
	rows, err := database.Pool.Query(ctx, "SELECT id, email, name, role, is_active, created_at FROM users ORDER BY created_at DESC")
	if err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to fetch users"})
	}
	defer rows.Close()

	var users []domain.User
	for rows.Next() {
		var u domain.User
		if err := rows.Scan(&u.ID, &u.Email, &u.Name, &u.Role, &u.IsActive, &u.CreatedAt); err != nil {
			continue
		}
		users = append(users, u)
	}

	if users == nil {
		users = []domain.User{}
	}
	return c.JSON(users)
}

// CreateUser adds a new user
func CreateUser(c fiber.Ctx) error {
	var input struct {
		Email    string `json:"email"`
		Password string `json:"password"`
		Name     string `json:"name"`
		Role     string `json:"role"`
	}

	if err := c.Bind().Body(&input); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
	}

	hashed, err := bcrypt.GenerateFromPassword([]byte(input.Password), 10)
	if err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to hash password"})
	}

	ctx := context.Background()
	var user domain.User
	err = database.Pool.QueryRow(ctx,
		"INSERT INTO users (email, password_hash, name, role) VALUES ($1, $2, $3, $4) RETURNING id, email, name, role, is_active, created_at",
		input.Email, string(hashed), input.Name, input.Role,
	).Scan(&user.ID, &user.Email, &user.Name, &user.Role, &user.IsActive, &user.CreatedAt)

	if err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to create user"})
	}

	return c.Status(fiber.StatusCreated).JSON(user)
}

// DeleteUser removes a user
func DeleteUser(c fiber.Ctx) error {
	id := c.Params("id")
	ctx := context.Background()

	command, err := database.Pool.Exec(ctx, "DELETE FROM users WHERE id = $1", id)
	if err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to delete user"})
	}
	if command.RowsAffected() == 0 {
		return c.Status(fiber.StatusNotFound).JSON(fiber.Map{"error": "User not found"})
	}

	return c.SendStatus(fiber.StatusNoContent)
}

// Login authenticates a user
func Login(c fiber.Ctx) error {
	var input struct {
		Email    string `json:"email"`
		Password string `json:"password"`
	}

	if err := c.Bind().Body(&input); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
	}

	ctx := context.Background()
	var user domain.User
	var hash string

	err := database.Pool.QueryRow(ctx, "SELECT id, email, password_hash, name, role, is_active FROM users WHERE email = $1", input.Email).Scan(
		&user.ID, &user.Email, &hash, &user.Name, &user.Role, &user.IsActive,
	)
	if err != nil {
		return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{"error": "Invalid credentials"})
	}

	if err := bcrypt.CompareHashAndPassword([]byte(hash), []byte(input.Password)); err != nil {
		return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{"error": "Invalid credentials"})
	}

	// Returning user info without token for now (Frontend manages session via context)
	return c.JSON(user)
}
