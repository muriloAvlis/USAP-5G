package logger

import (
	"os"
	"sync"

	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
)

var (
	sugar *zap.SugaredLogger
	once  sync.Once
)

// GetLogger returns a singleton instance of the logger
func GetLogger() *zap.SugaredLogger {
	once.Do(func() {
		stdout := zapcore.AddSync(os.Stdout)
		level := zap.NewAtomicLevelAt(zap.DebugLevel)
		loggerCfg := zap.NewProductionEncoderConfig()
		loggerCfg.EncodeTime = zapcore.ISO8601TimeEncoder
		loggerCfg.EncodeLevel = zapcore.CapitalColorLevelEncoder

		// Set color to logger (only development config)
		// loggerCfg.EncoderConfig.EncodeLevel = zapcore.CapitalColorLevelEncoder
		consoleEncoder := zapcore.NewConsoleEncoder(loggerCfg)

		core := zapcore.NewTee(
			zapcore.NewCore(consoleEncoder, stdout, level),
		)

		sugar = zap.New(core, zap.AddCaller()).Sugar()
	})
	return sugar
}

// Sync flushes any buffered log entries
// func Sync() {
// 	if logger != nil {
// 		_ = logger.Sync()
// 	}
// }
