package config

type Config struct {
	NodeID            string  `json:"nodeID"`
	DestinationNodeID string  `json:"destinationNodeID"`
	DefaultBandwidth  int     `json:"defaultBandwidth"`
	DefaultMaxDelay   int     `json:"defaultMaxDelay"`
	DefaultMaxLosses  float64 `json:"defaultMaxLosses"`

	ManagerAPIURL string `json:"managerAPIURL"`
}
