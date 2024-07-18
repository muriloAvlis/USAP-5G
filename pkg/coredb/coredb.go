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
		authSubsTable, err := cdb.getAuthSubs()
		// authSubsTable, err := cdb.getAuthSubsByUEId("01010101")
		queryTime := time.Since(queryTimeStart)
		time.Sleep(2 * time.Second)
		if err != nil {
			log.Println(err)
			continue
		}

		for _, v := range authSubsTable {
			fmt.Printf("UE-ID: %s\n", v.Ueid)
		}

		// fmt.Printf("UE-ID: %s\n", authSubsTable.Ueid)

		fmt.Printf("Query time: %s\n", queryTime)

		fmt.Println()
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
