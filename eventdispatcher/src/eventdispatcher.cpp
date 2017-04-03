#include <boost/python/module.hpp>
#include <boost/python/def.hpp>
#include <boost/python.hpp>
#include <boost/python/raw_function.hpp>


namespace bp = boost::python;


// Define an operator that works on boost::python::object
std::ostream& operator<<(std::ostream& os, const bp::object& o)
{
    return os << bp::extract<std::string>(bp::str(o))();
}


class cEventDispatcher : public bp::object {

	public:
        bp::dict event_dispatcher_properties;
        bp::list event_dispatcher_event_callbacks;

		// constructor function (equivalent to __init__ for python classes)
        cEventDispatcher() {
            std::cout <<  "call to C++ EventDispatcher constructor" << std::endl;
        }


		void __set__(bp::object obj, int value) {
			std::cout <<  "call to C++ __set__: " << value << std::endl;
		}



        void dispatch() {
            bp::list callbacks = this->event_dispatcher_event_callbacks;
            for (int ii=0; ii < len(callbacks); ii++)
                callbacks[ii]();
        }


};




class cProperty : bp::object {

	public:
        bp::object default_value;
        const char* name;
        //bp::str name;
        bp::dict instances;
        bp::object _additionals;

		// constructor function (equivalent to __init__ for python classes)
        cProperty(bp::object obj) {
            std::cout <<  "call to C++ Property constructor" << std::endl;
            this->default_value = obj;
        }

		bp::object __get__(cEventDispatcher obj, bp::object asd) {
            bp::object value;
			value = obj.event_dispatcher_properties[name]["value"];

			std::cout <<  "call to C++ __get__: " << value << std::endl;

			return value;
		}

		void __set__(cEventDispatcher obj, bp::object value) {
			std::cout <<  "call to C++ __set__: " << value << std::endl;

			if (obj.event_dispatcher_properties[name]["value"] != value) {
                obj.event_dispatcher_properties[name]["value"] = value;
                this->_dispatch(obj, value);
			}

		}


        void _dispatch(cEventDispatcher obj, bp::object value) {
            std::cout << "C++ DISPATCHING " << this->name << std::endl;

            for (int ii=0; ii < len(obj.event_dispatcher_properties[this->name]["callbacks"]); ii++) {
                const bp::object cb = bp::extract<bp::object>(obj.event_dispatcher_properties[this->name]["callbacks"][ii]);
                std::cout << cb << " : ";
                cb(obj, value);
                std::cout << std::endl;
            };

        }

        void register_(cEventDispatcher instance, const char* property_name, bp::object default_value) {
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





};



bp::object bind(bp::tuple args, bp::dict bindings) {
    bp::list keys = bindings.keys();
    cEventDispatcher eventdispatcher = bp::extract<cEventDispatcher>(args[0]);
    //std::cout << keys;
    for (int ii=0; ii<len(keys); ii++) {
        bp::object key = bp::extract<bp::str>(keys[ii]);
        bp::object value = bindings[key];
        std::cout << "Binding "<< key << " = " << value << std::endl;
        eventdispatcher.event_dispatcher_properties[key]["callbacks"].attr("append")(value);
    }
    return bp::object();

}


// See for explanation of using *args, **kwargs: https://wiki.python.org/moin/boost.python/HowTo#A.22Raw.22_function
bp::object cEventDispatcher_init(bp::tuple args, bp::dict kwargs) {
     std::cout <<  "call to c++ wrapped initializer" << std::endl;

     // strip off self
     std::cout <<  "Arugments to c++ wrapped initializer:" << std::endl;
     bp::object self = args[0];
     args = bp::tuple(args.slice(1, len(args)));
     for (int ii=0; ii< len(args); ii++) {
        const bp::object n = bp::extract<bp::object>(args[ii]);
        std::cout << n << std::endl;
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
        .def("__set__", &cEventDispatcher::__set__)
        .def("bind", raw_function(bind) )
        .def("dispatch", &cEventDispatcher::dispatch)
    ;

    class_<cProperty>("cProperty", init<object>())
        .def_readwrite("instances", &cProperty::instances)
        .def_readwrite("_additionals", &cProperty::_additionals)
        .def_readwrite("default_value", &cProperty::default_value)
        .def("__set__", &cProperty::__set__)
        .def("__get__", &cProperty::__get__)
        .def("register_", &cProperty::register_)
        .def("_dispatch", &cProperty::_dispatch)
        ;

}

