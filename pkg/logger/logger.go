package logger

import "gerrit.o-ran-sc.org/r/ric-plt/xapp-frame/pkg/xapp"

func SetLogger() {
	logger := xapp.NewLogger("usap-xapp")

	// logger configs
	logger.SetLevel(xapp.Config.GetInt("controls.logger.level"))
	logger.SetMdc("version", xapp.Config.GetString("appVersion"))

	xapp.Logger = logger
}
