package logger

import (
	"sync"

	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
)

var (
	logger *zap.Logger
	sugar  *zap.SugaredLogger
	once   sync.Once
)

// GetLogger returns a singleton instance of the logger
func GetLogger() *zap.SugaredLogger {
	once.Do(func() {
		var err error
		loggerCfg := zap.NewDevelopmentConfig()
		// Set color to logger
		loggerCfg.EncoderConfig.EncodeLevel = zapcore.CapitalColorLevelEncoder
		logger, err = loggerCfg.Build()
		if err != nil {
			panic(err)
		}

		sugar = logger.Sugar()
	})
	return sugar
}

// Sync flushes any buffered log entries
func Sync() {
	if logger != nil {
		_ = logger.Sync()
	}
}
