/*------------------------------------------------------------------------*/
/*----------------AuthenticationSubscription Table Handler----------------*/
/*------------------------------------------------------------------------*/

package coredb

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
)

// Default authentication values by OAI Core
var defaultAuthenticationSubData AuthenticationSubscriptionData = AuthenticationSubscriptionData{
	Ueid:                          "",
	AuthenticationMethod:          "5G_AKA",
	EncPermanentKey:               sql.NullString{String: "fec86ba6eb707ed08905757b1bb44b8f", Valid: true},
	ProtectionParameterId:         sql.NullString{String: "fec86ba6eb707ed08905757b1bb44b8f", Valid: true},
	SequenceNumber:                SequenceNumberData{Sqn: "000000000020", SqnScheme: "NON_TIME_BASED", LastIndexes: LastIndexesData{Ausf: 0}},
	AuthenticationManagementField: sql.NullString{String: "8000"},
	AlgorithmId:                   sql.NullString{String: "milenage"},
	EncOpcKey:                     sql.NullString{String: "C42449363BBAD02B66D16BC975D77CC1", Valid: true},
	EncTopcKey:                    sql.NullString{},
	VectorGenerationInHss:         sql.NullBool{},
	N5gcAuthMethod:                sql.NullString{},
	RgAuthenticationInd:           sql.NullBool{},
	Supi:                          sql.NullString{},
}

// Get all Authentication Subscriptions
func (cdb *coreDB) GetAuthSubs() ([]AuthenticationSubscriptionData, error) {
	var authSubs []AuthenticationSubscriptionData // stores table rows
	rows, err := cdb.dbHdlr.Query("SELECT * FROM AuthenticationSubscription")
	if err != nil {
		return nil, fmt.Errorf("unable to get informations from authenticationSubscription table: %s", err.Error())
	}
	defer rows.Close()

	var sequenceNumber sql.NullString // stores sequenceNumber json format

	for rows.Next() {
		var authSub AuthenticationSubscriptionData // stores table rown
		err = rows.Scan(
			&authSub.Ueid,
			&authSub.AuthenticationMethod,
			&authSub.EncPermanentKey,
			&authSub.ProtectionParameterId,
			&sequenceNumber,
			&authSub.AuthenticationManagementField,
			&authSub.AlgorithmId,
			&authSub.EncOpcKey,
			&authSub.EncTopcKey,
			&authSub.VectorGenerationInHss,
			&authSub.N5gcAuthMethod,
			&authSub.RgAuthenticationInd,
			&authSub.Supi,
		)
		if err != nil {
			return nil, fmt.Errorf("unable to get informations from authenticationSubscription table: %s", err.Error())
		}

		// Deserialize sequenceNumber data
		err = json.Unmarshal([]byte(sequenceNumber.String), &authSub.SequenceNumber)
		if err != nil {
			return nil, fmt.Errorf("error to process sequenceNumber column: %s", err.Error())
		}

		authSubs = append(authSubs, authSub) // add rown
	}

	if err = rows.Err(); err != nil {
		return nil, fmt.Errorf("unable to get informations from authenticationSubscription table: %s", err.Error())
	}

	return authSubs, nil // return table rows
}

// Get Authentication Subscription by UE ID
func (cdb *coreDB) GetAuthSub(ueId string) (AuthenticationSubscriptionData, error) {
	if len(ueId) != 15 {
		return AuthenticationSubscriptionData{}, fmt.Errorf("UE ID must be 15 digits")
	}

	var authSub AuthenticationSubscriptionData // store result
	// get row from AuthenticationSubscription Table
	row := cdb.dbHdlr.QueryRow("SELECT * FROM AuthenticationSubscription WHERE ueid = ?", ueId)

	var sequenceNumber sql.NullString // stores sequenceNumber json format

	err := row.Scan(
		&authSub.Ueid,
		&authSub.AuthenticationMethod,
		&authSub.EncPermanentKey,
		&authSub.ProtectionParameterId,
		&sequenceNumber,
		&authSub.AuthenticationManagementField,
		&authSub.AlgorithmId,
		&authSub.EncOpcKey,
		&authSub.EncTopcKey,
		&authSub.VectorGenerationInHss,
		&authSub.N5gcAuthMethod,
		&authSub.RgAuthenticationInd,
		&authSub.Supi,
	)

	if err != nil {
		if err == sql.ErrNoRows {
			return authSub, fmt.Errorf(
				"UE with ID %s not found on authenticationSubscription table: %s",
				ueId,
				err.Error(),
			)
		}
		return authSub, fmt.Errorf("unable to get ue informations from authenticationSubscription table: %s", err.Error())
	}

	// Deserialize sequenceNumber data
	err = json.Unmarshal([]byte(sequenceNumber.String), &authSub.SequenceNumber)
	if err != nil {
		return authSub, fmt.Errorf("error to process sequenceNumber column: %s", err.Error())
	}

	return authSub, nil
}

// Insert UE in AuthenticationSubscription table
func (cdb *coreDB) InsertAuthSub(ueId string) error {
	if len(ueId) != 15 {
		return fmt.Errorf("UE ID must be 15 digits")
	}

	// Prepare SQL to insert
	sqlInsert := `INSERT INTO AuthenticationSubscription
	 (ueid, authenticationMethod, encPermanentKey, protectionParameterId, sequenceNumber, authenticationManagementField,
	  algorithmId, encOpcKey, supi) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`

	seq_number_json, err := json.Marshal(defaultAuthenticationSubData.SequenceNumber)
	if err != nil {
		return fmt.Errorf("error to convert sequenceNumber to json: %s", err.Error())
	}

	// Exec SQL and replace values
	res, err := cdb.dbHdlr.Exec(sqlInsert,
		ueId,
		defaultAuthenticationSubData.AuthenticationMethod,
		defaultAuthenticationSubData.EncPermanentKey.String,
		defaultAuthenticationSubData.ProtectionParameterId.String,
		seq_number_json,
		defaultAuthenticationSubData.AuthenticationManagementField.String,
		defaultAuthenticationSubData.AlgorithmId.String,
		defaultAuthenticationSubData.EncOpcKey.String,
		ueId,
	)
	if err != nil {
		return fmt.Errorf("failed to insert UE authentication subscription into 5GC database: %s", err.Error())
	}

	rowsAffected, err := res.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to insert UE authentication subscription into 5GC database: %s ", err.Error())
	}

	if rowsAffected == 0 {
		return fmt.Errorf("failed to insert UE authentication subscription into 5GC database: %d rows affected", rowsAffected)
	}

	// UE inserted successfully
	log.Printf("UE with ID %s inserted with success into AuthenticationSubscription table\n", ueId)

	return nil
}

// Delete UE in AuthenticationSubscription table
func (cdb *coreDB) DeleteAuthSub(ueId string) error {
	if len(ueId) != 15 {
		return fmt.Errorf("UE ID must be 15 digits")
	}

	res, err := cdb.dbHdlr.Exec("DELETE FROM AuthenticationSubscription WHERE ueid = ?", ueId)

	if err != nil {
		return fmt.Errorf("failed to delete UE authentication subscription into 5GC database: %s", err.Error())
	}

	rowsAffected, err := res.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to delete UE authentication subscription into 5GC database: %s ", err.Error())
	}

	if rowsAffected == 0 {
		return fmt.Errorf("failed to delete UE authentication subscription into 5GC database: %d rows affected", rowsAffected)
	}

	// UE deleted successfully
	log.Printf("UE with ID %s deleted from AuthenticationSubscription table\n", ueId)

	return nil
}

// Delete all registers from AuthenticationSubscription table
func (cdb *coreDB) TruncateAuthSubs() error {
	_, err := cdb.dbHdlr.Exec("TRUNCATE TABLE AuthenticationSubscription")
	if err != nil {
		return fmt.Errorf("could not truncate table AuthenticationSubscription: %s", err.Error())
	}

	log.Printf("AuthenticationSubscription table successfully cleared!")

	return nil
}
