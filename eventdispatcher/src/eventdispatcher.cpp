#include <boost/python/module.hpp>
#include <boost/python/def.hpp>
#include <boost/python.hpp>
#include <boost/python/raw_function.hpp>

#include "eventdispatcher.h"
#include "property.h"
#include "listproperty.h"
#include "misc.h"

namespace bp = boost::python;


// constructor function (equivalent to __init__ for python classes)
cEventDispatcher::cEventDispatcher() {
    //std::cout <<  "call to C++ EventDispatcher constructor" << std::endl;
}



void cEventDispatcher::dispatch() {
    bp::list callbacks = this->event_dispatcher_event_callbacks;
    for (int ii=0; ii < len(callbacks); ii++)
        callbacks[ii]();
}


bp::object bind(bp::tuple args, bp::dict bindings) {
    bp::list keys = bindings.keys();
    cEventDispatcher eventdispatcher = bp::extract<cEventDispatcher>(args[0]);
    ////std::cout << keys;
    for (int ii=0; ii<len(keys); ii++) {
        bp::object key = bp::extract<bp::str>(keys[ii]);
        bp::object value = bindings[key];
        //std::cout << "Binding "<< key << " = " << value << std::endl;
        eventdispatcher.event_dispatcher_properties[key]["callbacks"].attr("append")(value);
    }
    return bp::object();

}


// See for explanation of using *args, **kwargs: https://wiki.python.org/moin/boost.python/HowTo#A.22Raw.22_function
bp::object cEventDispatcher_init(bp::tuple args, bp::dict kwargs) {
     //std::cout <<  "call to c++ wrapped initializer" << std::endl;

     // strip off self
     //std::cout <<  "Arugments to c++ wrapped initializer:" << std::endl;
     bp::object self = args[0];
     args = bp::tuple(args.slice(1, len(args)));
     for (int ii=0; ii< len(args); ii++) {
        const bp::object n = bp::extract<bp::object>(args[ii]);
        //std::cout << n << std::endl;
     }

     // call appropriate C++ constructor
     // depending on raw arguments, these
     // C++ constructors must be exposed to
     // Python through .def(init<...>())
     // declarations
     if (len(args) > 0) {
        return self.attr("__init__")();
     }

     return self.attr("__init__")(0);



}


BOOST_PYTHON_MODULE(eventdispatcher)
{
    using namespace boost::python;



	// Expose the class by wrapping it with the class_ template. The first argument is the name to expose it as and the second
	// argument is the constructor function. Pass no_init to postpone the defining of __init__ function under after raw_function.
	// This provides proper overloading resolution order since later defs get higher priority.
    class_<cEventDispatcher>("cEventDispatcher", no_init)
        .def("__init__", raw_function(cEventDispatcher_init), "raw constructor")
        .def(init<>())
        .def_readwrite("event_dispatcher_properties", &cEventDispatcher::event_dispatcher_properties)
        .def_readwrite("event_dispatcher_callbacks", &cEventDispatcher::event_dispatcher_event_callbacks)
        .def("bind", raw_function(bind) )
        .def("dispatch", &cEventDispatcher::dispatch)
    ;


    class_<cProperty>("cProperty", init<object>())
        .def_readwrite("instances", &cProperty::instances)
        .def_readwrite("_additionals", &cProperty::_additionals)
        .def_readwrite("default_value", &cProperty::default_value)
        .def("__set__", &cProperty::__set__<float>)
        .def("__set__", &cProperty::__set__<int>)
        .def("__get__", &cProperty::__get__)
        .def("register", &cProperty::register_property<float>)
        .def("register", &cProperty::register_property<int>)
        .def("register", &cProperty::register_property<cObservableList>)

        ;


    class_<cListProperty, bases<cProperty> >("cListProperty", init<object>())
        .def_readwrite("instances", &cListProperty::instances)
        .def_readwrite("_additionals", &cListProperty::_additionals)
        .def_readwrite("default_value", &cListProperty::default_value)
        .def("__set__", &cListProperty::__set__<list>)
        .def("__set__", &cListProperty::__set__<tuple>)
        .def("__get__", &cListProperty::__get__)
        .def("register", &cListProperty::register_property)
        ;

    class_<cObservableList>("cObservableList", init<list, cProperty*>())
        .def_readwrite("list", &cObservableList::list)
        ;



}

