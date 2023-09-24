package main

import (
	"encoding/json"
	"fmt"
	"os/exec"
	"strconv"
	"strings"

	"github.com/gin-gonic/gin"
)

func main() {
	g := gin.New()
	g.POST("/check", func(c *gin.Context) {
		fmt.Println("received check request")
		from, err := strconv.Atoi(c.Query("from"))
		if err != nil {
			c.JSON(400, gin.H{"error": err.Error()})
			return
		}
		to, err := strconv.Atoi(c.Query("to"))
		if err != nil {
			c.JSON(400, gin.H{"error": err.Error()})
			return
		}
		averageBandwidth, err := strconv.ParseFloat(c.Query("averageBandwidth"), 64)
		if err != nil {
			c.JSON(400, gin.H{"error": err.Error()})
			return
		}
		maxDelay, err := strconv.ParseFloat(c.Query("maxDelay"), 64)
		if err != nil {
			c.JSON(400, gin.H{"error": err.Error()})
			return
		}
		maxLosses, err := strconv.ParseFloat(c.Query("maxLosses"), 64)
		if err != nil {
			c.JSON(400, gin.H{"error": err.Error()})
			return
		}
		ok, err := checkFlow(from, to, averageBandwidth, maxDelay, maxLosses)
		if err != nil {
			c.JSON(500, gin.H{"error": err.Error()})
			return
		}
		if ok {
			c.JSON(200, gin.H{"ok": true})
		} else {
			c.JSON(200, gin.H{"ok": false})
		}
	})

	err := g.Run(":8080")
	if err != nil {
		fmt.Println(err)
	}

}

func checkFlow(from, to int, averageBandwidth float64, maxDelay, maxLosses float64) (bool, error) {
	trafficMatrix := [][]float64{
		{0, 0, 0, 0},
		{0, 0, 0, 0},
		{0, 0, 0, 0},
		{0, 0, 0, 0},
	}
	trafficMatrix[from][to] = averageBandwidth
	trafficMatrixJson, err := json.Marshal(trafficMatrix)
	if err != nil {
		return false, fmt.Errorf("error marshalling traffic matrix: %v", err)
	}
	if maxDelay >= 0 {
		out, err := exec.Command("sudo", "docker", "exec", "-w", "/home", "routenet", "python", "/home/main.py", "delay", string(trafficMatrixJson)).Output()
		if err != nil {
			return false, fmt.Errorf("error executing delay check: %v", err)
		}
		data := strings.Join(strings.Split(string(out), "\n")[1:], "")
		var arr [][]float64
		err = json.Unmarshal([]byte(data), &arr)
		if err != nil {
			return false, fmt.Errorf("error unmarshalling delay check: %v", err)
		}
		max := 0.
		for _, v := range arr {
			for _, v2 := range v {
				if v2 > maxDelay {
					fmt.Printf("the new flow will degrade the network due to delay (%f > %f), rejecting\n", v2, maxDelay)
					return false, nil
				}
				if v2 > max {
					max = v2
				}
			}
		}
		fmt.Printf("the new flow will increase the delay to %f\n", max)
	} else {
		fmt.Println("no requeriments for delay, skipping check")
	}

	if maxLosses >= 0 {
		out, err := exec.Command("sudo", "docker", "exec", "-w", "/home", "routenet", "python", "/home/main.py", "losses", string(trafficMatrixJson)).Output()
		if err != nil {
			return false, fmt.Errorf("error executing losses check: %v", err)
		}
		data := strings.Join(strings.Split(string(out), "\n")[1:], "")
		var arr [][]float64
		err = json.Unmarshal([]byte(data), &arr)
		if err != nil {
			return false, fmt.Errorf("error unmarshalling losses check: %v", err)
		}
		max := 0.
		for _, v := range arr {
			for _, v2 := range v {
				if v2 > maxLosses {
					fmt.Printf("the new flow will degrade the network due to losses (%f > %f), rejecting\n", v2, maxLosses)
					return false, nil
				}
				if v2 > max {
					max = v2
				}
			}
		}
		fmt.Printf("the new flow will increase the losses to %f\n", max)
	} else {
		fmt.Println("no requeriments for losses, skipping check")
	}

	fmt.Println("the new flow should not degrade the network, accepting")
	return true, nil
}
