package coredb

import (
	"database/sql"
	"encoding/json"
	"fmt"
)

// Get AuthenticationSubscription Table
func (cdb *coreDB) getAuthSubs() ([]AuthenticationSubscriptionTable, error) {
	var authSubs []AuthenticationSubscriptionTable // stores table rows
	rows, err := cdb.dbHdlr.Query("SELECT * FROM AuthenticationSubscription")
	if err != nil {
		return nil, fmt.Errorf("unable to get informations from authenticationSubscription table: %v", err)
	}
	defer rows.Close()

	var sequenceNumber sql.NullString // stores sequenceNumber json format

	for rows.Next() {
		var authSub AuthenticationSubscriptionTable // stores table rown
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
			return nil, fmt.Errorf("unable to get informations from authenticationSubscription table: %v", err)
		}

		// Deserialize sequenceNumber data
		err = json.Unmarshal([]byte(sequenceNumber.String), &authSub.SequenceNumber)
		if err != nil {
			return nil, fmt.Errorf("error to process sequenceNumber column: %v", err)
		}

		authSubs = append(authSubs, authSub) // add rown
	}

	if err = rows.Err(); err != nil {
		return nil, fmt.Errorf("unable to get informations from authenticationSubscription table: %v", err)
	}

	return authSubs, nil // return table rows
}

// Get AuthenticationSubscription Table by UE ID
func (cdb *coreDB) getAuthSubsByUEId(UeId string) (AuthenticationSubscriptionTable, error) {
	var authSub AuthenticationSubscriptionTable // store result
	// get row from AuthenticationSubscription Table
	row := cdb.dbHdlr.QueryRow("SELECT * FROM AuthenticationSubscription WHERE ueid = ?", UeId)

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
			return authSub, fmt.Errorf("ue with id %s not found on authenticationSubscription table: %v", UeId, err)
		}
		return authSub, fmt.Errorf("unable to get ue informations from authenticationSubscription table: %v", err)
	}

	// Deserialize sequenceNumber data
	err = json.Unmarshal([]byte(sequenceNumber.String), &authSub.SequenceNumber)
	if err != nil {
		return authSub, fmt.Errorf("error to process sequenceNumber column: %v", err)
	}

	return authSub, nil
}
