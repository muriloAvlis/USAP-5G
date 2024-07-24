package coredb

import (
	"database/sql"
	"fmt"
	"log"
	"time"

	"github.com/go-sql-driver/mysql"
)

func NewManager(config Config) *coreDB {
	if config == (Config{}) {
		log.Fatal("The database configuration cannot be empty!")
	}

	// test 5GC DB connection
	db, err := connect(config)
	if err != nil {
		log.Fatal(err)
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
	db.SetConnMaxLifetime(2 * time.Minute)
	db.SetMaxOpenConns(10)
	db.SetMaxIdleConns(10)

	// test DB connection
	err = db.Ping()
	if err != nil {
		return nil, fmt.Errorf("error to connect with 5GC database: %v", err)

	}

	log.Println("Connected to 5GC database!")
	return db, nil
}

// Run operations on the 5GC Database
func (cdb *coreDB) Run() {
	if err := cdb.start(); err != nil {
		log.Fatal(err)
		cdb.dbHdlr.Close() // close DB conn
	}
}

// Start 5GC DB processes
func (cdb *coreDB) start() error {
	// In development
	for {
		queryTimeStart := time.Now()
		authSubsTable, err := cdb.getAuthSubs()
		queryTime := time.Since(queryTimeStart)
		time.Sleep(2 * time.Second)
		if err != nil {
			return fmt.Errorf("unable to run 5gc db operation: %v", err)
		}

		for _, v := range authSubsTable {
			log.Printf("UE-ID: %s\n", v.Ueid)
		}

		log.Printf("Query time: %s\n", queryTime)
	}
}
