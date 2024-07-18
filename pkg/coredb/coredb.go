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

// Run operations on the 5GC Database
func (cdb *coreDB) Run() {
	// In development
	for {
		queryTimeStart := time.Now()
		AuthSubsTable, err := cdb.getAuthenticationSubscription()
		queryTime := time.Since(queryTimeStart)
		if err != nil {
			log.Println(err)
		}

		for _, v := range AuthSubsTable {
			fmt.Printf("UE-ID: %s\n", v.Ueid)
		}
		fmt.Printf("Query time: %s\n", queryTime)

		fmt.Println()

		time.Sleep(2 * time.Second)
	}
}

func connect(config Config) (*sql.DB, error) {
	// organizing DB config
	cfg := mysql.Config{
		User:   config.CoreDBUser,
		Passwd: config.CoreDBPassword,
		Net:    "tcp",
		Addr:   config.CoreDBAddress + ":" + config.CoreDBPort,
		DBName: config.CoreDBName,
	}

	// Get a database handle.
	db, err := sql.Open("mysql", cfg.FormatDSN())
	if err != nil {
		return nil, fmt.Errorf("error to open database connetion: %v", err)
	}

	// test DB connection
	err = db.Ping()
	if err != nil {
		return nil, fmt.Errorf("error to connect with database: %v", err)

	}

	fmt.Println("Connected to 5GC database!")
	return db, nil
}
