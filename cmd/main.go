package main

import (
	"context"
	"fmt"
	"time"

	"github.com/muriloAvlis/qmai/internal/checkErr"
	"github.com/muriloAvlis/qmai/pkg/e2Connectivity"
)

const (
	e2Addr   = "onos-e2t"                 // e2 address (change this for deploy to k8s)
	e2NodeID = "e2:4/e00/2/64"            // e2 node ID
	subName  = "onos-kpimon-subscription" // subscription name
	appName  = "qmai"
)

func main() {
	// creates a E2 client
	client := e2Connectivity.NewE2Client(e2Addr)

	// get E2 node
	e2node := e2Connectivity.GetE2Node(client, e2NodeID)
	fmt.Println(e2node)

	// creates a report subscription
	subSpec := e2Connectivity.NewReportSubscription()

	// creates a indication channel
	ch := e2Connectivity.NewIndicationChannel()

	// creates a context to subscription with timeout
	ctx, cancel := context.WithTimeout(context.Background(), time.Minute)
	defer cancel()

	// creates the subscribe
	_, err := e2node.Subscribe(ctx, subName, subSpec, ch)

	// check error
	checkErr.Check(err)

	// prints KPIs
	for ind := range ch {
		fmt.Println(ind)
	}

	// Cancel the subscription
	err = e2node.Unsubscribe(ctx, subName)
	checkErr.Check(err)
}
