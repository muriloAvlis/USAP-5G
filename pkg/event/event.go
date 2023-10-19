package event

// Event store event data structure
type Event struct {
	Key   interface{}
	Value interface{}
	Type  interface{}
}
