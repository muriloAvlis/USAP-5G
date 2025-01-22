package rnib

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"strings"

	"gerrit.o-ran-sc.org/r/ric-plt/xapp-frame/pkg/xapp"
	"github.com/muriloAvlis/usap-5g/pkg/utils"
)

// Get eNBs list
func geteNBList() ([]*xapp.RNIBNbIdentity, error) {
	eNBs, err := xapp.Rnib.GetListEnbIds()
	if err != nil {
		xapp.Logger.Error("Unable to get eNodeB list: %s", err.Error())
		return nil, err
	}

	var eNB_names []string
	for _, eNB := range eNBs {
		eNB_names = append(eNB_names, eNB.GetInventoryName())
	}

	xapp.Logger.Info("List of connected eNodeBs: [%s]", strings.Join(eNB_names, ", "))

	return eNBs, nil
}

// Get gNBs list
func getgNBList() ([]*xapp.RNIBNbIdentity, error) {
	gNBs, err := xapp.Rnib.GetListGnbIds()
	if err != nil {
		xapp.Logger.Error("Unable to get gNodeB list: %s", err.Error())
		return nil, err
	}

	var gNB_names []string
	for _, gNB := range gNBs {
		gNB_names = append(gNB_names, gNB.GetInventoryName())
	}

	xapp.Logger.Info("List of connected gNodeBs: [%s]", strings.Join(gNB_names, ", "))

	return gNBs, nil
}

// Get gNB and eNB list connected to RIC
func GetNbList() []*xapp.RNIBNbIdentity {
	var nodeBs []*xapp.RNIBNbIdentity

	if eNBs, err := geteNBList(); err == nil {
		nodeBs = append(nodeBs, eNBs...)
	}

	if gNBs, err := getgNBList(); err == nil {
		nodeBs = append(nodeBs, gNBs...)
	}

	return nodeBs
}

func GetRanFuncDefiniton(inventoryName string, ranFuncId int64) (string, error) {
	uri := "http://" + os.Getenv("E2MGR_HTTP_SERVICE_HOST") + ":" + os.Getenv("E2MGR_HTTP_SERVICE_PORT") + "/v1/nodeb/" + inventoryName

	response, err := http.Get(uri)
	if err != nil {
		return "", fmt.Errorf("failed to get E2 node informations from E2MGR: %s", err.Error())
	}
	defer response.Body.Close()

	// Decode E2 node response
	var e2Response E2mgrResponse
	err = json.NewDecoder(response.Body).Decode(&e2Response)
	if err != nil {
		return "", fmt.Errorf("failed to decode E2 node informations from E2MGR: %s", err.Error())
	}

	// check if E2 Node has KPM RAN function == 2
	rfIdx := -1
	for idx, rf := range e2Response.Gnb.RanFunctions {
		if rf.RanFunctionId == ranFuncId {
			rfIdx = idx
			xapp.Logger.Debug("E2 node %s has KPM RF index: %d", inventoryName, rfIdx)
		}
	}

	if rfIdx == -1 {
		return "", fmt.Errorf("e2 node %s does not have KPM RF, finalizing KPI extraction proccess", inventoryName)
	}

	return e2Response.Gnb.RanFunctions[rfIdx].RanFunctionDefinition, nil
}

func GetMeasNameList(ranFuncDefinition map[string]interface{}, reportStyleType int) []string {
	var measNameList []string

	reportStyles := ranFuncDefinition["ric-ReportStyle-List"].([]interface{})

	for _, reportStyle := range reportStyles {
		reportStyleMap := reportStyle.(map[string]interface{})

		styleTypeInt := utils.FloatInterfaceToInt(reportStyleMap["ric-ReportStyle-Type"])

		if styleTypeInt == reportStyleType {
			measList := reportStyleMap["measInfo-Action-List"].([]interface{})
			for _, meas := range measList {
				measMap := meas.(map[string]interface{})
				measNameList = append(measNameList, measMap["measName"].(string))
			}
		}
	}

	return measNameList
}

func GetDuId(inventoryName string) (string, error) {
	uri := "http://" + os.Getenv("E2MGR_HTTP_SERVICE_HOST") + ":" + os.Getenv("E2MGR_HTTP_SERVICE_PORT") + "/v1/nodeb/" + inventoryName

	response, err := http.Get(uri)
	if err != nil {
		return "", fmt.Errorf("failed to get E2 node informations from E2MGR: %s", err.Error())
	}
	defer response.Body.Close()

	// Decode E2 node response
	var e2Response E2mgrResponse
	err = json.NewDecoder(response.Body).Decode(&e2Response)
	if err != nil {
		return "", fmt.Errorf("failed to decode E2 node informations from E2MGR: %s", err.Error())
	}

	// check if E2 Node has KPM RAN function == 2
	if e2Response.DuId == "" {
		return "", fmt.Errorf("e2 node %s has no DU ID", inventoryName)
	}

	return e2Response.DuId, nil
}

// Função para inverter uma string
func ReverseString(input string) string {
	runes := []rune(input)
	for i, j := 0, len(runes)-1; i < j; i, j = i+1, j-1 {
		runes[i], runes[j] = runes[j], runes[i]
	}
	return string(runes)
}

// Decode PLMN and return MCC and MNC
func DecodePLMN(plmn string) string {
	var mcc, mnc string

	if strings.Contains(plmn, "F") {
		// ABFCDE
		// BACF -> BAC (MCC)
		mcc = ReverseString(plmn[0:2]) + strings.ReplaceAll(ReverseString(plmn[2:4]), "F", "")

		// Invert 2 last digits (MNC)
		mnc = ReverseString(plmn[4:6])
	} else {
		// ABCDEF
		// ABCD -> BAD (MCC)
		mcc = ReverseString(plmn[0:2]) + ReverseString(string(plmn[3]))

		// FE + D (MNC)
		mnc = ReverseString(plmn[4:6]) + string(ReverseString(string(plmn[2]))[0])
	}

	return mcc + mnc // plmn
}
