package logging

import "gerrit.o-ran-sc.org/r/ric-plt/xapp-frame/pkg/xapp"

func GetLogger() *xapp.Log {
	logger := xapp.NewLogger("USAP-xApp")
	// logger configs
	logger.SetLevel(xapp.Config.GetInt("controls.logger.level"))
	logger.SetMdc("VERSION", "v1.0.0-alpha")

	return logger
}
