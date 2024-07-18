package coredb

import "database/sql"

// Object to handle coredb functionalities
type coreDB struct {
	dbHdlr *sql.DB
	Config
}

// DB Configs
type Config struct {
	CoreDBUser     string
	CoreDBPassword string
	CoreDBAddress  string
	CoreDBPort     string
	CoreDBName     string
}

// Tables

// --- AuthenticationSubscription Table --- //
type AuthenticationSubscriptionTable struct {
	Ueid                          string
	AuthenticationMethod          string
	EncPermanentKey               sql.NullString
	ProtectionParameterId         sql.NullString
	SequenceNumber                SequenceNumberData
	AuthenticationManagementField sql.NullString
	AlgorithmId                   sql.NullString
	EncOpcKey                     sql.NullString
	EncTopcKey                    sql.NullString
	VectorGenerationInHss         sql.NullBool
	N5gcAuthMethod                sql.NullString
	RgAuthenticationInd           sql.NullBool
	Supi                          sql.NullString
}

type SequenceNumberData struct {
	Sqn         string
	SqnScheme   string
	LastIndexes LastIndexesData
}

type LastIndexesData struct {
	Ausf uint8
}
