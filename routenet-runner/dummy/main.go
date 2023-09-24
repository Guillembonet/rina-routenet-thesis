package main

import (
	"fmt"
	"os"
	"strings"
)

func main() {
	fmt.Println("called: ", strings.Join(os.Args, ","))
	os.Exit(0)
}
