package main

import (
	"fmt"
	"time"
)

func main() {
	timestamp := float64(time.Now().UnixMilli())
	fmt.Printf("%.0f\n", timestamp)
}
