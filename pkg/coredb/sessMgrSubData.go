/*-------------------------------------------------------------------------*/
/*-------------SessionManagementSubscriptionData Table Handler-------------*/
/*-------------------------------------------------------------------------*/

package coredb

import (
	"database/sql"
	"encoding/json"
	"fmt"
)

// Default S-NSSAI configuration
var defaultSingleNssai singleNssaiData = singleNssaiData{Sst: 128, Sd: "000001"}

// Default DNN configuration
var defaultDnnConfigData dnnConfigurationsData = map[string]dnnConfigurationsDataValues{
	"nongbr": {
		PduSessionTypes: pduSessionTypesData{DefaultSessionType: "IPV4V6"},
		SscModes:        sscModesData{DefaultSscMode: "SSC_MODE_1"},
		FiveGQosProfile: fiveGQosProfileData{FiveQI: 9, Arp: arpData{PriorityLevel: 15, PreemptCap: "NOT_PREEMPT", PreemptVuln: "PREEMPTABLE"}, PriorityLevel: 1},
		SessionAmbr:     sessionAmbrData{Uplink: "10Mbps", Downlink: "10Mbps"},
		StaticIpAddress: []*staticIpAddressData{},
	},
}

// Get all Session Subscription Data from UEs
func (cdb *coreDB) GetSubscriptionsData() ([]SessionManagementSubscriptionData, error) {
	var subsData []SessionManagementSubscriptionData // stores table rows
	rows, err := cdb.dbHdlr.Query("SELECT * FROM SessionManagementSubscriptionData")
	if err != nil {
		return nil, fmt.Errorf("error to get UEs session subscription data: %s", err.Error())
	}
	defer rows.Close()

	var singleNssaiVal, dnnConfigurationsVal sql.NullString // stores json format

	for rows.Next() {
		var subData SessionManagementSubscriptionData
		err = rows.Scan(
			&subData.Ueid,
			&subData.ServingPlmnid,
			&singleNssaiVal,
			&dnnConfigurationsVal,
			&subData.InternalGroupIds,
			&subData.SharedVnGroupDataIds,
			&subData.SharedDnnConfigurationsId,
			&subData.OdbPacketServices,
			&subData.TraceData,
			&subData.SharedTraceDataId,
			&subData.ExpectedUeBehavioursList,
			&subData.SuggestedPacketNumDlList,
			&subData.ThreegppChargingCharacteristics,
		)
		if err != nil {
			return nil, fmt.Errorf("error to get UE session subscription data: %s", err.Error())
		}

		// Deserialize singleNssaiVal on struct format
		err = json.Unmarshal([]byte(singleNssaiVal.String), &subData.SingleNssai)
		if err != nil {
			return nil, fmt.Errorf("error to process singleNssai data: %s", err.Error())
		}

		// Deserialize dnnConfigurationsVal on struct format
		err = json.Unmarshal([]byte(dnnConfigurationsVal.String), &subData.DnnConfigurations)
		if err != nil {
			return nil, fmt.Errorf("error to process dnnConfigurations data: %s", err.Error())
		}

		subsData = append(subsData, subData) // add rown
	}
	if err = rows.Err(); err != nil {
		return nil, fmt.Errorf("unable to get UEs session subscription data: %s", err.Error())
	}

	return subsData, nil // return table rows
}

// Get Session Subscription Data by UE ID
func (cdb *coreDB) GetSubscriptionData(ueId string) (SessionManagementSubscriptionData, error) {
	var subData SessionManagementSubscriptionData // store result

	// check if UE ID is valid
	if len(ueId) != 15 {
		return subData, fmt.Errorf("UE ID must be 15 digits")
	}

	// get row from SessionManagementSubscriptionData Table
	row := cdb.dbHdlr.QueryRow("SELECT * FROM SessionManagementSubscriptionData WHERE ueid = ?", ueId)

	var singleNssaiVal, dnnConfigurationsVal sql.NullString // stores json format

	err := row.Scan(
		&subData.Ueid,
		&subData.ServingPlmnid,
		&singleNssaiVal,
		&dnnConfigurationsVal,
		&subData.InternalGroupIds,
		&subData.SharedVnGroupDataIds,
		&subData.SharedDnnConfigurationsId,
		&subData.OdbPacketServices,
		&subData.TraceData,
		&subData.SharedTraceDataId,
		&subData.ExpectedUeBehavioursList,
		&subData.SuggestedPacketNumDlList,
		&subData.ThreegppChargingCharacteristics,
	)

	if err != nil {
		if err == sql.ErrNoRows {
			return subData, fmt.Errorf("UE session subscription data with ID %s not found: %s", ueId, err.Error())
		}
		return subData, fmt.Errorf("unable to get UE session subscription data: %s", err.Error())
	}

	// Deserialize singleNssaiVal on struct format
	err = json.Unmarshal([]byte(singleNssaiVal.String), &subData.SingleNssai)
	if err != nil {
		return subData, fmt.Errorf("error to process singleNssai column: %s", err.Error())
	}

	// Deserialize dnnConfigurationsVal on struct format
	err = json.Unmarshal([]byte(dnnConfigurationsVal.String), &subData.DnnConfigurations)
	if err != nil {
		return subData, fmt.Errorf("error to process dnnConfigurations column: %s", err.Error())
	}

	return subData, nil
}

// Insert UE in SessionManagementSubscriptionData table
func (cdb *coreDB) InsertSubscriptionData(subData *SessionManagementSubscriptionData) error {
	// UE ID = IMSI = MCC + MNC + MSIN
	if len(subData.Ueid) != 15 {
		return fmt.Errorf("UE ID must be 15 digits")
	}

	// PLMD ID = MCC + MNC
	if len(subData.ServingPlmnid) != 5 && len(subData.ServingPlmnid) != 6 {
		return fmt.Errorf("PLMN must be 5 or 6 digits")
	}

	// Prepare SQL to insert
	sqlInsert := `INSERT INTO SessionManagementSubscriptionData
	 (ueid, servingPlmnid, singleNssai, dnnConfigurations) VALUES (?, ?, ?, ?)`

	// checks if no S-NSSAI has been configured in the subscription
	if subData.SingleNssai == (singleNssaiData{}) {
		subData.SingleNssai = defaultSingleNssai
	}

	// Serialize singleNssai on json format
	singleNssaiJson, err := json.Marshal(subData.SingleNssai)
	if err != nil {
		return fmt.Errorf("error to convert sequenceNumber to json: %s", err.Error())
	}

	// checks if no DNN has been configured in the subscription
	if len(subData.DnnConfigurations) == 0 {
		subData.DnnConfigurations = defaultDnnConfigData
	}

	// Serialize singleNssai on json format
	dnnConfigurationsJson, err := json.Marshal(subData.DnnConfigurations)
	if err != nil {
		return fmt.Errorf("error to convert DNN configurations to json: %s", err.Error())
	}

	// Exec SQL and replace values
	res, err := cdb.dbHdlr.Exec(sqlInsert,
		subData.Ueid,
		subData.ServingPlmnid,
		singleNssaiJson,
		dnnConfigurationsJson,
	)
	if err != nil {
		return fmt.Errorf("failed to insert UE session subscription data into 5GC database: %s", err.Error())
	}

	rowsAffected, err := res.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to insert UE session subscription data into 5GC database: %s ", err.Error())
	}

	if rowsAffected == 0 {
		return fmt.Errorf("failed to insert UE session subscription data into 5GC database: %d rows affected", rowsAffected)
	}

	// UE inserted successfully
	logger.Info("UE session subscription data with ID %s created with success!\n", subData.Ueid)

	return nil
}

// Update UE session subscription data
func (cdb *coreDB) UpdateSubscriptionData(subData *SessionManagementSubscriptionData) error {
	// UE ID = IMSI = MCC + MNC + MSIN
	if len(subData.Ueid) != 15 {
		return fmt.Errorf("UE ID must be 15 digits")
	}

	// PLMD ID = MCC + MNC
	if len(subData.ServingPlmnid) != 5 && len(subData.ServingPlmnid) != 6 {
		return fmt.Errorf("PLMN must be 5 or 6 digits")
	}

	// Prepare SQL to insert
	sqlUpdate := `UPDATE SessionManagementSubscriptionData SET
		singleNssai = ?, dnnConfigurations = ? WHERE ueid = ? AND servingPlmnid = ?`

	// Serialize singleNssai on json format
	singleNssaiJson, err := json.Marshal(subData.SingleNssai)
	if err != nil {
		return fmt.Errorf("error to convert sequenceNumber to json: %s", err.Error())
	}

	// checks if no DNN has been configured in the subscription
	if len(subData.DnnConfigurations) == 0 {
		subData.DnnConfigurations = defaultDnnConfigData
	}

	// Serialize singleNssai on json format
	dnnConfigurationsJson, err := json.Marshal(subData.DnnConfigurations)
	if err != nil {
		return fmt.Errorf("error to convert DNN configurations to json: %s", err.Error())
	}

	// Exec SQL and replace values
	res, err := cdb.dbHdlr.Exec(
		sqlUpdate,
		singleNssaiJson,
		dnnConfigurationsJson,
		subData.Ueid,
		subData.ServingPlmnid,
	)
	if err != nil {
		return fmt.Errorf("failed to update UE session subscription data into 5GC database: %s", err.Error())
	}

	rowsAffected, err := res.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to update UE session subscription data into 5GC database: %s ", err.Error())
	}

	if rowsAffected == 0 {
		return fmt.Errorf("failed to update UE session subscription data into 5GC database: %d rows affected", rowsAffected)
	}

	// UE updated successfully
	logger.Info("UE session subscription data with ID %s updated with success!\n", subData.Ueid)

	return nil
}

// Delete UE into SessionManagementSubscriptionData table
func (cdb *coreDB) DeleteSubscriptionData(ueId string) error {
	if len(ueId) != 15 {
		return fmt.Errorf("UE ID must be 15 digits")
	}

	res, err := cdb.dbHdlr.Exec("DELETE FROM SessionManagementSubscriptionData WHERE ueid = ?", ueId)

	if err != nil {
		return fmt.Errorf("failed to delete UE session subscription data into 5GC database: %s", err.Error())
	}

	rowsAffected, err := res.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to delete UE session subscription data into 5GC database: %s ", err.Error())
	}

	if rowsAffected == 0 {
		return fmt.Errorf("failed to delete UE session subscription data into 5GC database: %d rows affected", rowsAffected)
	}

	// UE deleted successfully
	logger.Info("UE session subscription data with ID %s deleted with success!\n", ueId)

	return nil
}

// Delete all registers from SessionManagementSubscriptionData table
func (cdb *coreDB) TruncateSubscriptionData() error {
	_, err := cdb.dbHdlr.Exec("TRUNCATE TABLE SessionManagementSubscriptionData")
	if err != nil {
		return fmt.Errorf("could not truncate table SessionManagementSubscriptionData: %s", err.Error())
	}

	logger.Info("SessionManagementSubscriptionData table successfully cleared!")

	return nil
}
