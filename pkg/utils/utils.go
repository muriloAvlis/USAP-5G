package utils

func FloatInterfaceToInt(value interface{}) int {
	if v, ok := value.(float64); ok {
		return int(v)
	}
	return 0 // return 0 if fail
}
