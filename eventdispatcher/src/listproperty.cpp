#include <boost/python/module.hpp>
#include <boost/python/def.hpp>
#include <boost/python.hpp>
#include <boost/python/slice.hpp>
#include <boost/python/raw_function.hpp>

#include "eventdispatcher.h"
#include "listproperty.h"
#include "misc.h"

namespace bp = boost::python;


template <typename T> bool check_equal_sequences(bp::list sequence_A, T sequence_B) {
    if (len(sequence_A) != len(sequence_B)) {
        return true;
    } else {
        for (int ii=0; ii < len(sequence_A); ii++) {
            if (sequence_A[ii] != sequence_B[ii]) {
                return true;
                }
        }
        return false;
    }
};


template <typename T> void cListProperty::__set__(cEventDispatcher obj, T value) {
//    std::cout <<  "call to cListProperty C++ __set__: " << std::endl;
bp::list l = bp::extract<bp::list>(obj.event_dispatcher_properties[name]["value"].attr("list"));
    if (check_equal_sequences(l, value)) {
        del(l[bp::slice()]);
        l.extend(value);
        this->dispatch(obj, l);
    }
};


// Explicitly instantiate template functions so that the compiler can create their definition and
// We can expose them to python
template void cListProperty::__set__<bp::list>(cEventDispatcher obj, bp::list value);
template void cListProperty::__set__<bp::tuple>(cEventDispatcher obj, bp::tuple value);

template void cObservableList::extend<bp::tuple>(bp::tuple values);
template void cObservableList::extend<bp::list>(bp::list values);
