package manager

import (
	appConfig "github.com/muriloAvlis/qmai/pkg/config"
	"github.com/muriloAvlis/qmai/pkg/southbound/e2"
	uemgr "github.com/muriloAvlis/qmai/pkg/uenib"
	"github.com/onosproject/onos-lib-go/pkg/logging"
)

// manager configuration
type Config struct {
	AppID        string
	CAPath       string
	KeyPath      string
	CertPath     string
	E2tEndpoint  string
	E2tPort      int
	TopoEndpoint string
	TopoPort     int
	ConfigPath   string
	SMName       string
	SMVersion    string
}

// Manager is an abstract struct for manager
type Manager struct {
	appConfig appConfig.Config
	config    Config
	E2Manager e2.Manager
}

// initializes package log
var log = logging.GetLogger("qmai", "manager")

// new xAPP manager
func NewManager(config Config) *Manager {
	// initializes app configuration
	appCfg, err := appConfig.NewConfig(config.ConfigPath)
	if err != nil {
		log.Warn(err)
	}

	// creates a e2Config
	e2Config := e2.Config{
		AppID:       config.AppID,
		AppConfig:   appCfg,
		E2tAddress:  config.E2tEndpoint,
		E2tPort:     config.E2tPort,
		TopoAddress: config.TopoEndpoint,
		TopoPort:    config.TopoPort,
		SMName:      config.SMName,
		SMVersion:   config.SMVersion,
	}
	// creates a new E2 Manager
	e2Manager, err := e2.NewManager(e2Config)

	if err != nil {
		log.Warn(err)
	}

	// creates a UE-NIB Manager
	ueManager, err := uemgr.NewClient()
	if err != nil {
		log.Warn(err)
	}
	log.Info(ueManager)

	manager := &Manager{
		appConfig: appCfg,
		config:    config,
		E2Manager: e2Manager,
	}

	return manager
}

// runs xAPP
func (m *Manager) Run() {
	if err := m.start(); err != nil {
		log.Errorf("Unable when starting Manager: %v", err)
	}
}

// starts xAPP processes
func (m *Manager) start() error {
	// E2 subscriptions
	err := m.E2Manager.Start()

	// UE-NiB (TODO)

	if err != nil {
		log.Warn(err)
		return err
	}
	return nil
}

// finalizes xApp processes
func (m *Manager) Close() {
	// TODO
	// syscall.Kill(syscall.Getpid(), syscall.SIGINT)
}
