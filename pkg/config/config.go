package config

import (
	"strings"

	"gerrit.o-ran-sc.org/r/ric-plt/xapp-frame/pkg/xapp"
	"github.com/muriloAvlis/usap-5g/pkg/utils"
)

func GetReportStyleType() int {
	var reportStyleType int
	serviceModels := xapp.Config.Get("controls.subscription.e2sm").([]interface{})

	for _, sm := range serviceModels {
		smStruct := sm.(map[string]interface{})

		if strings.ToUpper(smStruct["name"].(string)) == "KPM" {
			reportStyleType = utils.FloatInterfaceToInt(smStruct["report_style_type"])
		}

	}
	return reportStyleType
}

func GetReportingPeriod() int64 {
	var reportingPeriod int
	serviceModels := xapp.Config.Get("controls.subscription.e2sm").([]interface{})

	for _, sm := range serviceModels {
		smStruct := sm.(map[string]interface{})

		if strings.ToUpper(smStruct["name"].(string)) == "KPM" {
			reportingPeriod = utils.FloatInterfaceToInt(smStruct["reporting_period"])
		}

	}
	return int64(reportingPeriod)
}

func GetGranularityPeriod() int64 {
	var granularityPeriod int
	serviceModels := xapp.Config.Get("controls.subscription.e2sm").([]interface{})

	for _, sm := range serviceModels {
		smStruct := sm.(map[string]interface{})

		if strings.ToUpper(smStruct["name"].(string)) == "KPM" {
			granularityPeriod = utils.FloatInterfaceToInt(smStruct["granularity_period"])
		}

	}
	return int64(granularityPeriod)
}

func IsEmulated() bool {
	return xapp.Config.GetBool("controls.emulatedScenario")
}

func GetUEImsiList() []string {
	serviceModels := xapp.Config.Get("controls.subscription.e2sm").([]interface{})
	ueImsiList := make([]string, 0, 10)

	for _, sm := range serviceModels {
		smStruct := sm.(map[string]interface{})

		if strings.ToUpper(smStruct["name"].(string)) == "KPM" {
			ueList := smStruct["ue_list"].([]interface{})
			for _, ue := range ueList {
				ueStruct := ue.(map[string]interface{})
				ueImsiList = append(ueImsiList, ueStruct["imsi"].(string))
			}
		}

	}

	return ueImsiList
}
