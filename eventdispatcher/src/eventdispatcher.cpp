#include <boost/python/module.hpp>
#include <boost/python/def.hpp>
#include <boost/python.hpp>
#include <boost/python/raw_function.hpp>


namespace bp = boost::python;

char const* help()
{
   return "This is where the help would go if I wasn't lazy";
}


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

        void bind(bp::object f) {
            this->event_dispatcher_event_callbacks.append(f);
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

		void __set__(bp::object obj, bp::object value) {
			std::cout <<  "call to C++ __set__: " << value << std::endl;
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

    def("help", help);


	// Expose the class by wrapping it with the class_ template. The first argument is the name to expose it as and the second
	// argument is the constructor function. Pass no_init to postpone the defining of __init__ function under after raw_function.
	// This provides proper overloading resolution order since later defs get higher priority.
    class_<cEventDispatcher>("cEventDispatcher", no_init)
        .def("__init__", raw_function(cEventDispatcher_init), "raw constructor")
        .def(init<>())
        .def_readwrite("event_dispatcher_properties", &cEventDispatcher::event_dispatcher_properties)
        .def_readwrite("event_dispatcher_callbacks", &cEventDispatcher::event_dispatcher_event_callbacks)
        .def("__set__", &cEventDispatcher::__set__)			// expose the defined a class method
        .def("bind", &cEventDispatcher::bind)			// expose the defined a class method
        .def("dispatch", &cEventDispatcher::dispatch)			// expose the defined a class method
    ;

    class_<cProperty>("cProperty", init<object>())
        .def_readwrite("instances", &cProperty::instances)
        .def_readwrite("_additionals", &cProperty::_additionals)
        .def_readwrite("default_value", &cProperty::default_value)
        .def("__set__", &cProperty::__set__)			// expose the defined a class method
        .def("__get__", &cProperty::__get__)			// expose the defined a class method
        .def("register_", &cProperty::register_)			// expose the defined a class method
        ;

}

