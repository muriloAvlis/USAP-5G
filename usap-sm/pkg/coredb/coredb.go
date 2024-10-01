package coredb

import (
	"database/sql"
	"fmt"
	"time"

	"github.com/go-sql-driver/mysql"
	"github.com/muriloAvlis/usap-5g/usap-sm/pkg/logger"
)

var log = logger.GetLogger()

func NewManager(config Config) *coreDB {
	if config == (Config{}) {
		log.Error("The database configuration cannot be empty!")
	}

	// establish 5GC DB connection
	db, err := connect(config)
	for err != nil {
		log.Error(err.Error())
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

	log.Infof("Connected to 5GC database %s:%s", config.CoreDBAddress, config.CoreDBPort)
	return db, nil
}

// Clean up tables used by Application
func (cdb *coreDB) cleanTables() error {
	// Clean up tables used by Application
	err := cdb.TruncateAuthSubs() // Authentication Table
	if err != nil {
		return err
	}

	err = cdb.TruncateSubscriptionData() // Subscription Table
	if err != nil {
		return err
	}

	return nil
}

// Run operations on the 5GC Database
func (cdb *coreDB) Run() {
	if err := cdb.start(); err != nil {
		log.Error(err.Error())
		cdb.dbHdlr.Close() // close DB conn
	}
}

// Start 5GC DB processes
func (cdb *coreDB) start() error {
	// clean tables for experiment (do it just on dev env)
	err := cdb.cleanTables()
	if err != nil {
		return err
	}

	// Add initial UEs to default slice (It's a test)
	//// UE-0
	err = cdb.InsertAuthSub("724700000000001") // Authentication Table
	if err != nil {
		return err
	}

	subsData := SessionManagementSubscriptionData{
		Ueid:              "724700000000001",
		ServingPlmnid:     "72470",
		SingleNssai:       defaultSingleNssai,
		DnnConfigurations: defaultDnnConfigData,
	}
	err = cdb.InsertSubscriptionData(&subsData) // Subscription table
	if err != nil {
		return err
	}

	// TODO: Create a gRPC server to receive subscriptions data
	return nil
}
