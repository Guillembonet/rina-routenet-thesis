package config

type Config struct {
	NodeID            string `json:"nodeID"`
	DestinationNodeID string `json:"destinationNodeID"`

	ManagerAPIURL string `json:"managerAPIURL"`
}
