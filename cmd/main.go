package main

import (
	"context"
	"time"

	"github.com/muriloAvlis/qmai/internal/checkErr"
	"github.com/muriloAvlis/qmai/pkg/e2Connectivity"
	"github.com/onosproject/onos-lib-go/pkg/logging"
)

type sdranValues struct {
	e2Addr     string // e2 address (change this for deploy to k8s)
	e2GrpcPort int    // e2 node ID
	e2NodeID   string // e2 Node ID (TODO: get it automatic)
	subName    string // subscription name
	appName    string // app name
}

var log = logging.GetLogger("qmai")

func main() {
	// defines E2 configs
	config := sdranValues{
		e2Addr:     "192.168.254.3",
		e2GrpcPort: 35150,
		e2NodeID:   "e2:4/e00/2/64",
		subName:    "onos-kpimon-subscription",
		appName:    "qmai",
	}

	// creates a E2 client
	client := e2Connectivity.NewE2Client(config.e2Addr, config.e2GrpcPort, config.appName)

	// get E2 node
	e2node := e2Connectivity.GetE2Node(client, config.e2NodeID)
	log.Infof("E2 Node: %v", e2node)

	// creates a report subscription
	subSpec := e2Connectivity.NewReportSubscription()
	log.Infof("Subscription Specification: %v", subSpec)

	// creates a indication channel
	ch := e2Connectivity.NewIndicationChannel()

	// creates a context to subscription with timeout
	ctx, cancel := context.WithTimeout(context.Background(), time.Minute)
	defer cancel()

	// creates the subscribe
	_, err := e2node.Subscribe(ctx, config.subName, subSpec, ch)

	// check error
	checkErr.Check(err)

	// prints KPIs
	for ind := range ch {
		log.Info(ind)
	}

	// Cancel the subscription
	err = e2node.Unsubscribe(ctx, config.subName)
	checkErr.Check(err)
}
