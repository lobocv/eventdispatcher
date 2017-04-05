#include <boost/python/module.hpp>
#include <boost/python/def.hpp>
#include <boost/python.hpp>
#include <boost/python/raw_function.hpp>

#include "eventdispatcher.h"
#include "property.h"
#include "misc.h"

namespace bp = boost::python;


cProperty::cProperty(bp::object obj) {
    std::cout <<  "call to C++ Property constructor" << std::endl;
    this->default_value = obj;
}

bp::object cProperty::__get__(cEventDispatcher obj, bp::object asd) {
    bp::object value;
    value = obj.event_dispatcher_properties[name]["value"];

    std::cout <<  "call to C++ __get__: " << value << std::endl;

    return value;
}

void cProperty::__set__(cEventDispatcher obj, bp::object value) {
    std::cout <<  "call to C++ __set__: " << value << std::endl;

    if (obj.event_dispatcher_properties[name]["value"] != value) {
        obj.event_dispatcher_properties[name]["value"] = value;
        this->_dispatch(obj, value);
    }
}


void cProperty::_dispatch(cEventDispatcher obj, bp::object value) {
    std::cout << "C++ DISPATCHING " << this->name << std::endl;

    for (int ii=0; ii < len(obj.event_dispatcher_properties[this->name]["callbacks"]); ii++) {
        const bp::object cb = bp::extract<bp::object>(obj.event_dispatcher_properties[this->name]["callbacks"][ii]);
        std::cout << cb << " : ";
        cb(obj, value);
        std::cout << std::endl;
    };

}

void cProperty::register_(cEventDispatcher instance, const char* property_name, bp::object default_value) {
    bp::dict info;
    bp::list callback_list;

    this->name = property_name;
    info["property"] = this;
    info["value"] = default_value;
    info["name"] = property_name;
    info["callbacks"] = callback_list;

    this->instances[instance] = info;
    instance.event_dispatcher_properties[property_name] = info;
}

