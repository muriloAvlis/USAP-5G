package coredb

import (
	"database/sql"
	"encoding/json"
	"fmt"
)

// Get AuthenticationSubscription Table
func (cdb *coreDB) getAuthenticationSubscription() ([]AuthenticationSubscriptionTable, error) {
	var AuthSubs []AuthenticationSubscriptionTable // stores table rows
	rows, err := cdb.dbHdlr.Query("SELECT * FROM AuthenticationSubscription")
	if err != nil {
		return nil, fmt.Errorf("unable to get informations from authenticationSubscription table: %v", err)
	}
	defer rows.Close()

	var SequenceNumber sql.NullString // stores SequenceNumber json format

	for rows.Next() {
		var AuthSub AuthenticationSubscriptionTable // stores table rown
		err = rows.Scan(
			&AuthSub.Ueid,
			&AuthSub.AuthenticationMethod,
			&AuthSub.EncPermanentKey,
			&AuthSub.ProtectionParameterId,
			&SequenceNumber,
			&AuthSub.AuthenticationManagementField,
			&AuthSub.AlgorithmId,
			&AuthSub.EncOpcKey,
			&AuthSub.EncTopcKey,
			&AuthSub.VectorGenerationInHss,
			&AuthSub.N5gcAuthMethod,
			&AuthSub.RgAuthenticationInd,
			&AuthSub.Supi,
		)
		if err != nil {
			return nil, fmt.Errorf("unable to get informations from authenticationSubscription table: %v", err)
		}

		// Deserialize SequenceNumber data
		err = json.Unmarshal([]byte(SequenceNumber.String), &AuthSub.SequenceNumber)
		if err != nil {
			return nil, fmt.Errorf("error to process sequenceNumber column: %v", err)
		}

		AuthSubs = append(AuthSubs, AuthSub) // add rown
	}

	if err = rows.Err(); err != nil {
		return nil, fmt.Errorf("unable to get informations from authenticationSubscription table: %v", err)
	}

	return AuthSubs, nil // return table rows
}
