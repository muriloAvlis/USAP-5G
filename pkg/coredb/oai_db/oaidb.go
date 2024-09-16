package oaidb

import (
	"database/sql"
	"fmt"
	"sync"
	"time"

	"gerrit.o-ran-sc.org/r/ric-plt/xapp-frame/pkg/xapp"
	"github.com/go-sql-driver/mysql"
)

func NewManager(config Config) *coreDB {
	if config == (Config{}) {
		xapp.Logger.Error("The database configuration cannot be empty!")
	}

	// establish 5GC DB connection
	db, err := connect(config)
	for err != nil {
		xapp.Logger.Error(err.Error())
		time.Sleep(5 * time.Second) // retry connection after 5 sec
		db, err = connect(config)
	}

	return &coreDB{
		dbHdlr: db,
		Config: config,
	}
}

// Open a connection with 5GC database
func connect(config Config) (*sql.DB, error) {
	// organizing DB config
	cfg := mysql.Config{
		User:   config.CoreDBUser,
		Passwd: config.CoreDBPassword,
		Net:    "tcp",
		Addr:   config.CoreDBAddress + ":" + config.CoreDBPort,
		DBName: config.CoreDBName,
	}

	// Get a database handler.
	db, err := sql.Open("mysql", cfg.FormatDSN())
	if err != nil {
		return nil, fmt.Errorf("error to open database connetion: %v", err)
	}

	// Set important connection configs
	db.SetConnMaxLifetime(1 * time.Minute)
	db.SetMaxOpenConns(100)
	db.SetMaxIdleConns(100)

	// test DB connection
	err = db.Ping()
	if err != nil {
		return nil, fmt.Errorf("error to connect with 5GC database: %v", err)

	}

	xapp.Logger.Info("Connected to 5GC database!")
	return db, nil
}

// Run operations on the 5GC Database
func (cdb *coreDB) Run(wg *sync.WaitGroup) {
	if err := cdb.start(); err != nil {
		defer wg.Done()
		xapp.Logger.Error(err.Error())
		cdb.dbHdlr.Close() // close DB conn
	}
}

// Start 5GC DB processes
func (cdb *coreDB) start() error {
	// Clean up tables used by App (TODO: review this comportament)
	err := cdb.TruncateAuthSubs() // Authentication Table
	if err != nil {
		return err
	}

	err = cdb.TruncateSubscriptionData() // Subscription Table
	if err != nil {
		return err
	}

	// Add initial UEs to default slice
	//// UE-0
	cdb.InsertAuthSub("724700000000001") // Authentication Table
	if err != nil {
		return err
	}

	subsData := SessionManagementSubscriptionData{
		Ueid:              "724700000000001",
		ServingPlmnid:     "72470",
		SingleNssai:       defaultSingleNssai,
		DnnConfigurations: defaultDnnConfigData,
	}
	cdb.InsertSubscriptionData(&subsData) // Subscription table
	if err != nil {
		return err
	}

	// Show status of UEs connected to 5GC (TODO)
	return nil
}
