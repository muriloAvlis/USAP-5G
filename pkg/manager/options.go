package manager

import (
	appConfig "github.com/muriloAvlis/qmai/pkg/config"
	"github.com/muriloAvlis/qmai/pkg/southbound/e2"
	uemgr "github.com/muriloAvlis/qmai/pkg/uemgr"
)

// manager configuration
type Config struct {
	AppID         string
	CAPath        string
	KeyPath       string
	CertPath      string
	E2tEndpoint   string
	E2tPort       int
	TopoEndpoint  string
	TopoPort      int
	UeNibEndpoint string
	UeNibPort     int
	ConfigPath    string
	SMName        string
	SMVersion     string
}

// Manager is an abstract struct for manager
type Manager struct {
	appConfig appConfig.Config
	config    Config
	E2Manager e2.Manager
	UeManager uemgr.Manager
}
