package coredb

import (
	"database/sql"
	"errors"
	"fmt"
	"net"
	"sync"
	"time"

	"gerrit.o-ran-sc.org/r/ric-plt/xapp-frame/pkg/xapp"
	"github.com/go-sql-driver/mysql"
	"github.com/muriloAvlis/USAP/pkg/logging"
)

var logger xapp.Log = *logging.GetLogger()

func NewManager(config Config) *coreDB {
	if config == (Config{}) {
		logger.Error("The database configuration cannot be empty!")
	}

	// establish 5GC DB connection
	db, err := connect(config)
	for err != nil {
		logger.Error(err.Error())
		time.Sleep(1 * time.Second) // retry connection after 1 sec
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

	logger.Info("Connected to 5GC database!")
	return db, nil
}

// Run operations on the 5GC Database
func (cdb *coreDB) Run(wg *sync.WaitGroup) {
	if err := cdb.start(); err != nil {
		defer wg.Done()
		logger.Error(err.Error())
		cdb.dbHdlr.Close() // close DB conn
	}
}

// Start 5GC DB processes
func (cdb *coreDB) start() error {
	// Clean up tables used by App (TODO: review this comportament)
	err := cdb.TruncateAuthSubs()
	if err != nil {
		return err
	}

	err = cdb.TruncateSubscriptionData()
	if err != nil {
		return err
	}

	// Show status of UEs connected to 5GC (TODO)
	return nil
}

func GetDBIpbyHostname(coreDBHostname string) (string, error) {
	coreDBAddr := net.ParseIP(coreDBHostname)
	if coreDBAddr != nil { // it is already IP format
		return coreDBAddr.String(), nil
	} else { // convert to IPv4 format
		dbIpAddr, err := net.LookupIP(coreDBHostname)
		if err != nil {
			return "", err
		}

		for _, dbIp := range dbIpAddr {
			if dbIp.To4() != nil { // first IPv4 occurrence // TODO: review this comportament
				return dbIp.To4().String(), nil
			}
		}
	}
	return "", errors.New("unable to get 5GC Database IP Address")
}
