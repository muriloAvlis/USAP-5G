package main

import (
	"os"
	"os/signal"
	"sync"
	"syscall"

	"github.com/muriloAvlis/usap-5g/usap-xapp/pkg/kpimon"
	"github.com/muriloAvlis/usap-5g/usap-xapp/pkg/logger"
	"github.com/muriloAvlis/usap-5g/usap-xapp/pkg/server"
)

var (
	log = logger.GetLogger()
	wg  sync.WaitGroup
)

// FIXME: Not working with FlexRIC SDK
func signalHandler() chan os.Signal {
	stopSig := make(chan os.Signal, 1)
	signal.Notify(stopSig, syscall.SIGINT, syscall.SIGTERM)

	// wait for stop signal
	go func() {
		sig := <-stopSig
		log.Warnf("Received a stop signal %v, stopping xApp...", sig)
	}()

	return stopSig
}

func main() {
	defer log.Sync()
	log.Info("Starting USAP-xApp | VERSION 0.0.1")

	// start Signal Handler
	stopSig := signalHandler()

	// start KPM monitor
	kpmConf := kpimon.Config{
		StopSignal: stopSig,
	}
	monitor := kpimon.NewManager(kpmConf)
	wg.Add(1)
	go func() { // launch a Monitor Go routine
		defer wg.Done()

		monitor.Run()
	}()

	// start gRPC server
	serverConf := server.Config{
		IndCh: monitor.IndCh,
	}
	s := server.NewManager(serverConf)
	wg.Add(1)
	go func() { // lauch a gRPC server Go routine
		defer wg.Done()
		s.Run()
	}()

	// Wait for stop signal
	<-stopSig

	log.Info("Waiting for all processes to stop...")
	wg.Wait()
	log.Info("USAP-xApp finish with successfully!")
}
