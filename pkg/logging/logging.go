package logging

import (
	"gerrit.o-ran-sc.org/r/ric-plt/xapp-frame/pkg/xapp"
)

// TODO: with issues
func GetLogger() *xapp.Log {
	logger := xapp.NewLogger("usap-xapp")

	// logger configs
	logger.SetLevel(xapp.Config.GetInt("controls.logger.level"))

	return logger
}
