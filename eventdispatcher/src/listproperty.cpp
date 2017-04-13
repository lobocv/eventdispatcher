#include <boost/python/module.hpp>
#include <boost/python/def.hpp>
#include <boost/python.hpp>
#include <boost/python/raw_function.hpp>

#include "eventdispatcher.h"
#include "listproperty.h"
#include "misc.h"

namespace bp = boost::python;


template <typename T> bool compare_sequences(bp::list sequence_A, T sequence_B) {
    return true;
};


template <typename T> void cListProperty::__set__(cEventDispatcher obj, T value) {
    std::cout <<  "call to cListProperty C++ __set__: " << std::endl;
//    if (compare_sequences(obj.event_dispatcher_properties[name]["value"], value)) {
    if (obj.event_dispatcher_properties[name]["value"].attr("list") != value) {
        obj.event_dispatcher_properties[name]["value"].attr("list") = bp::list(value);
        this->dispatch(obj, value);
    }
};


// Explicitly instantiate template functions so that the compiler can create their definition and
// We can expose them to python
template void cListProperty::__set__<bp::list>(cEventDispatcher obj, bp::list value);
template void cListProperty::__set__<bp::tuple>(cEventDispatcher obj, bp::tuple value);

