#ifndef PROPERTY_INCLUDED
#define PROPERTY_INCLUDED

#include <boost/python/module.hpp>
#include <boost/python/def.hpp>
#include <boost/python.hpp>
#include <boost/python/raw_function.hpp>


namespace bp = boost::python;



class cProperty : public bp::object {

	public:
        const char* name;
        bp::object default_value;
        bp::dict instances;
        bp::object _additionals;

        cProperty(bp::object obj);

		bp::object __get__(cEventDispatcher obj, bp::object asd);

		template <typename T> void __set__(cEventDispatcher obj, T value);

        void register_property(cEventDispatcher instance, const char* property_name, bp::object default_value);

    private:
        void dispatch(cEventDispatcher obj, int value) ;
        void dispatch(cEventDispatcher obj, float value) ;




};

#endif // PROPERTY_INCLUDED
