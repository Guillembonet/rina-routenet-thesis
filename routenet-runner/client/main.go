package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/guillembonet/routenet-runner/client/config"
)

func main() {
	configPath := flag.String("c", "/home/irati/config.json", "Path to config file")
	flag.Parse()
	fmt.Println(*configPath)
	args := flag.Args()
	fmt.Println(strings.Join(args, ","))
	if len(args) < 3 || args[0] == "" || args[1] == "" || args[2] == "" {
		fmt.Println("Usage: routenet <averageBandwidth> <maxDelay> <maxLosses>")
		os.Exit(0)
	}
	averageBandwidth := args[0]
	maxDelay := args[1]
	maxLosses := args[2]

	file, err := os.Open(*configPath)
	if err != nil {
		fmt.Println(err)
		os.Exit(0)
	}

	var cfg config.Config
	err = json.NewDecoder(file).Decode(&cfg)
	if err != nil {
		fmt.Println(err)
		os.Exit(0)
	}

	req, err := http.NewRequest("POST", fmt.Sprintf("%s/check", strings.TrimSuffix(cfg.ManagerAPIURL, "/")), nil)
	if err != nil {
		fmt.Println(err)
		os.Exit(0)
	}
	q := req.URL.Query()
	q.Add("from", cfg.NodeID)
	q.Add("to", "2")
	q.Add("averageBandwidth", averageBandwidth)
	q.Add("maxDelay", maxDelay)
	q.Add("maxLosses", maxLosses)
	req.URL.RawQuery = q.Encode()

	client := &http.Client{
		Timeout: 30 * time.Second,
	}
	resp, err := client.Do(req)
	if err != nil {
		fmt.Println(err)
		os.Exit(0)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if resp.StatusCode != http.StatusOK {
		var errResp errorResponse
		err = json.Unmarshal(body, &errResp)
		if err != nil {
			fmt.Println("The flow check failed, and the error response couldn't be parsed", err)
			os.Exit(0)
		}
		fmt.Println("The flow check failed, will accept flow:", errResp.Error)
		os.Exit(0)
	}

	var checkResp checkResponse
	err = json.Unmarshal(body, &checkResp)
	if err != nil {
		fmt.Println("The flow check succeded, but the response couldn't be parsed", err)
		os.Exit(0)
	}
	if !checkResp.Ok {
		fmt.Println("The flow check succeded, but the response was not ok")
		os.Exit(1)
	}
	fmt.Println("The flow check succeded, will accept flow")
	os.Exit(0)
}

type errorResponse struct {
	Error string `json:"error"`
}

type checkResponse struct {
	Ok bool `json:"ok"`
}
